"""FastAPI entrypoint: python -m uvicorn main:app --reload"""
import copy
import base64
import hashlib
import os
import mimetypes
import re
import secrets
import time
from contextlib import closing
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
from Content import ROUNDS
from question_content import DeckError, load_rounds, validate_rounds, deck_bytes, text_presentation, classification_context, MEDIA_EXTENSIONS, MEDIA_FOLDERS, is_public_icebreaker_blob
from store import Store
from global_deck import get_shared_deck, put_shared_deck
from deck_bundle_import import (MAX_ZIP, read_bundle, collect_assets, upload_assets, substitute_assets)

app = FastAPI(title="AI or Human", docs_url=None, redoc_url=None, openapi_url=None)
store = Store()
MAX_PLAYERS = 200
BASE_POINTS = 100          # EDIT scoring here.
STREAK_STEP = 25           # 2nd consecutive correct answer earns +25.
MAX_STREAK_BONUS = 100     # 5th+ consecutive correct answer earns +100.
ROOM_LIFETIME_HOURS = 12


class CreateRoom(BaseModel):
    title: str = Field(default="AI or Human", min_length=1, max_length=60)
    seconds: int = Field(default=25, ge=5, le=120)
    password: str = Field(default="", max_length=256)
    deck: list[dict] | None = Field(default=None, max_length=200)


class JoinRoom(BaseModel):
    nickname: str = Field(min_length=1, max_length=24)


class CreateTeam(BaseModel):
    name: str = Field(min_length=1, max_length=40)


class Vote(BaseModel):
    answer: Literal["AI", "HUMAN"]
    round_index: int = Field(ge=0)


class Control(BaseModel):
    action: Literal["start", "next", "begin_voting"]
    revision: int = Field(ge=0)


def digest(token):
    return hashlib.sha256(token.encode()).hexdigest()


def credential(authorization):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "A game token is required. Rejoin the room.")
    return digest(authorization[7:])


def identity(state, authorization):
    key = credential(authorization)
    if secrets.compare_digest(key, state["host"]):
        return "host", None
    for player_id, player in state["players"].items():
        if secrets.compare_digest(key, player["token"]):
            return "player", player_id
    raise HTTPException(401, "This browser session does not belong to this room.")


def room_code(code):
    code = code.upper()
    if not re.fullmatch(r"[A-Z2-9]{6}", code):
        raise HTTPException(400, "Enter a six-character room code.")
    return code


def join_link(request, code):
    base = os.getenv("PUBLIC_BASE_URL", "").rstrip("/") or str(request.base_url).rstrip("/")
    return f"{base}/?room={code}"


def qr_payload(link):
    """Generate locally; encode only the public join link, never game credentials."""
    import qrcode
    from qrcode.image.svg import SvgPathFillImage
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=10, border=4)
    qr.add_data(link)
    qr.make(fit=True)
    svg = qr.make_image(image_factory=SvgPathFillImage).to_string()
    return {"join_url": link, "qr_matrix": qr.get_matrix(),
            # Retain the image field for older presenter tabs during a redeploy.
            "qr_data_uri": "data:image/svg+xml;base64," + base64.b64encode(svg).decode("ascii")}


POOL_SECONDS = 3


def pool_votes(state):
    """Freeze one answer per team. Ties and no votes are abstentions."""
    pooled = {}
    for tid in state.get("teams", {}):
        member_ids = [pid for pid, p in state["players"].items() if p.get("team_id") == tid]
        counts = {choice: sum(state["votes"].get(pid, {}).get("answer") == choice
                              for pid in member_ids) for choice in ("AI", "HUMAN")}
        answer = "AI" if counts["AI"] > counts["HUMAN"] else "HUMAN" if counts["HUMAN"] > counts["AI"] else None
        pooled[tid] = {"answer": answer, "counts": counts, "voted": sum(counts.values()),
                       "member_count": len(member_ids), "tie": counts["AI"] == counts["HUMAN"] and counts["AI"] > 0}
    return pooled


def score_round(state):
    answer = state["rounds"][state["index"]]["answer"]
    if state.get("teams"):
        for tid, tally in state["team_results"].items():
            team = state["teams"][tid]
            correct = tally["answer"] == answer
            team["streak"] = team.get("streak", 0) + 1 if correct else 0
            points = BASE_POINTS + min((team["streak"] - 1) * STREAK_STEP, MAX_STREAK_BONUS) if correct else 0
            team["score"] = team.get("score", 0) + points
            team["correct"] = team.get("correct", 0) + int(correct)
            team.setdefault("history", []).append({"round": state["index"] + 1,
                "answer": tally["answer"], "correct": correct, "points": points})
        # Unassigned users cannot contribute to any team's score.
        for pid, player in state["players"].items():
            if player.get("team_id") in state["teams"]:
                team = state["teams"][player["team_id"]]
                player["score"] = team["score"]
                player["streak"] = team["streak"]
                player["correct"] = team["correct"]
                player["history"] = list(team["history"])
    else:
        # Legacy rooms without teams keep their individual scoring behavior.
        for player_id, player in state["players"].items():
            if player["joined_at"] > state["deadline"]:
                continue
            vote = state["votes"].get(player_id)
            correct = bool(vote and vote["answer"] == answer)
            player["streak"] = player["streak"] + 1 if correct else 0
            points = BASE_POINTS + min((player["streak"] - 1) * STREAK_STEP, MAX_STREAK_BONUS) if correct else 0
            player["score"] += points
            player["correct"] += int(correct)
            player["history"].append({"round": state["index"] + 1, "answer": vote["answer"] if vote else None,
                                      "correct": correct, "points": points})
    state["phase"] = "revealed"
    state["revision"] += 1


def round_seconds(state):
    """A deck question may override the presenter's room-wide voting duration.

    Old rooms/decks without seconds retain the configured room duration.
    The snapshot is validated on room creation; never trust client clock values.
    """
    question = state['rounds'][state['index']]
    local = question.get('seconds')
    return local if question.get('timer_mode') == 'local' and isinstance(local, int) and not isinstance(local, bool) and 5 <= local <= 120 else state['default_seconds']


def settle(state):
    """Server-authoritative voting -> pooling -> reveal, exactly once per transition."""
    now = time.time()
    if state["phase"] == "live" and now >= state["deadline"]:
        if state.get("teams"):
            state["team_results"] = pool_votes(state)
            state["phase"] = "pooling"
            state["pool_deadline"] = now + POOL_SECONDS
            state["revision"] += 1
        else:
            score_round(state)
    if state["phase"] == "pooling" and now >= state["pool_deadline"]:
        score_round(state)


def view(state, role, player_id):
    players = sorted(state["players"].items(), key=lambda pair: (-pair[1]["score"], pair[1]["nickname"].casefold(), pair[0]))
    board = []
    last_score, rank = None, 0
    for position, (pid, player) in enumerate(players, 1):
        if player["score"] != last_score:
            rank = position
        last_score = player["score"]
        board.append({"id": pid, "nickname": player["nickname"], "score": player["score"],
                      "streak": player["streak"], "correct": player["correct"], "rank": rank})
    teams = []
    for tid, team in state.get("teams", {}).items():
        creator = state["players"][team["creator_id"]]
        members = [{"id": pid, "nickname": player["nickname"]}
                   for pid, player in state["players"].items() if player.get("team_id") == tid]
        members.sort(key=lambda p: p["id"] != team["creator_id"])
        teams.append({"id": tid, "name": team["name"],
                      "creator": {"id": team["creator_id"], "nickname": creator["nickname"]},
                      "members": members})
    team_board = []
    for tid, team in state.get("teams", {}).items():
        team_board.append({"id": tid, "nickname": team["name"], "score": team.get("score", 0),
                           "streak": team.get("streak", 0), "correct": team.get("correct", 0),
                           "members": len(next(t["members"] for t in teams if t["id"] == tid))})
    team_board.sort(key=lambda t: (-t["score"], t["nickname"].casefold(), t["id"]))
    for position, item in enumerate(team_board):
        item["rank"] = 1 + next(i for i, t in enumerate(team_board) if t["score"] == item["score"])
    result = {"code": state["code"], "title": state["title"], "phase": state["phase"],
              "round_index": state["index"], "round_number": state["index"] + 1,
              "round_count": len(state["rounds"]), "revision": state["revision"],
              "server_time": time.time(), "deadline": state["deadline"],
              "duration": state["duration"], "player_count": len(players),
              "answered_count": len(state["votes"]), "leaderboard": team_board if state.get("teams") else board, "question": None,
              "pool_deadline": state.get("pool_deadline") if state["phase"] == "pooling" else None,
              "team_results": state.get("team_results", {}) if state["phase"] == "revealed" else {},
              "me": None, "reveal": None,
              "teams_enabled": "teams" in state,
              "teams_open": "teams" in state and state["phase"] == "lobby", "teams": teams}
    if state["phase"] in ("watching", "live", "pooling", "revealed"):
        question = state["rounds"][state["index"]]
        result["question"] = {k: question[k] for k in
                              ("title", "kind", "body", "media", "alt", "image_fit", "image_position",
                               "media_url", "media_start", "media_end", "difficulty", "context", "text_style", "news") if k in question}
        if question["kind"] == "text":
            # Resolve presentation for snapshots created before the format field.
            # Keep the saved room content and private answer fields untouched.
            result["question"]["text_style"] = text_presentation(question)
        if "context" in result["question"]:
            result["question"]["context"] = classification_context(result["question"]["context"])
        if state["phase"] == "revealed":
            result["reveal"] = {k: question[k] for k in
                                ("answer", "explanation", "source", "source_url", "technical_note",
                                 "discussion", "technical_source_url", "image_reveal",
                                 "image_highlight", "reveal_sources", "reveal_media", "reveal_alt") if k in question}
            result["reveal"]["distribution"] = {
                choice: sum(v["answer"] == choice for v in state["votes"].values()) for choice in ("AI", "HUMAN")}
    if player_id:
        player = state["players"][player_id]
        result["me"] = {**next(row for row in board if row["id"] == player_id),
                        "team_id": player.get("team_id"),
                        "vote": state["votes"].get(player_id, {}).get("answer"),
                        "history": player["history"]}
        if player.get("team_id") in state.get("teams", {}):
            result["me"]["rank"] = next(t["rank"] for t in team_board if t["id"] == player["team_id"])
    return result


@app.middleware("http")
async def response_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    if request.url.path.startswith("/api/") or response.headers.get("content-type", "").startswith("text/html"):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(Exception)
async def failure(request, error):
    # Do not echo database URLs/passwords in browser responses or application logs.
    return JSONResponse(status_code=503, content={"detail": "Service unavailable. Check database setup and try again."})


@app.get("/")
def player_page():
    return FileResponse(ROOT / "static/index.html")


@app.get("/presenter")
def presenter_page():
    return FileResponse(ROOT / "static/presenter.html")


@app.get("/bonus")
def bonus_page():
    """Standalone, unscored question after the final podium."""
    return FileResponse(ROOT / "static/bonus.html")


@app.get("/api/health")
def health():
    with closing(store.connect()) as connection:
        connection.execute("SELECT 1")
        # Check that the migration and grants are actually ready, without changing data.
        if store.url:
            connection.execute("SELECT code FROM icebreaker.rooms LIMIT 0")
    return {"status": "ok", "storage": "Supabase PostgreSQL" if store.url else "local SQLite"}


@app.get("/api/integration/capabilities")
def integration_capabilities():
    """Used to detect IceBreaker versions that accept Organizer-edited decks."""
    return {"version": 2, "room_deck": True, "seminar_host_handoff": True, "shared_deck": True, "vercel_blob_media": True}


@app.post("/api/rooms")
def create_room(body: CreateRoom, request: Request):
    password = os.getenv("PRESENTER_PASSWORD", "")
    if os.getenv("VERCEL") and not password:
        raise HTTPException(503, "Set PRESENTER_PASSWORD in Vercel before creating a game.")
    if password and not secrets.compare_digest(body.password.encode(), password.encode()):
        raise HTTPException(403, "Presenter password is incorrect.")
    try:
        rounds = validate_rounds(body.deck, ROOT) if body.deck is not None else validate_rounds(get_shared_deck(store, load_rounds(ROOT, fallback=ROUNDS))["rounds"], ROOT)
    except DeckError as error:
        source = "questions.json" if (ROOT / "questions.json").exists() else "Content.py starter deck; questions.json is absent"
        raise HTTPException(503, f"Question deck cannot load ({source}): {error} Save a valid deck in the manager and include its media files in the app or deployment.") from error
    if not rounds or any(r.get("answer") not in ("AI", "HUMAN") or r.get("kind") not in
                         ("code", "commit", "text", "image", "audio", "video") for r in rounds):
        raise HTTPException(503, "Fix the round definitions in Content.py.")
    token = secrets.token_urlsafe(32)
    for _ in range(5):
        code = "".join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(6))
        state = {"code": code, "title": body.title.strip() or "AI or Human", "host": digest(token),
                 "join_url": join_link(request, code),
                 "expires_at": time.time() + ROOM_LIFETIME_HOURS * 3600, "players": {},
                 "rounds": copy.deepcopy(rounds), "phase": "lobby", "index": 0, "revision": 0,
                 "deadline": None, "duration": body.seconds, "default_seconds": body.seconds, "votes": {},
                 "teams": {}}
        if store.create(code, state):
            return {"code": code, "token": token, "join_url": state["join_url"],
                    "deck_hash": hashlib.sha256(deck_bytes(rounds)).hexdigest()}
    raise HTTPException(503, "Could not allocate a room. Try again.")


@app.get("/api/rooms/{code}/qr")
def room_qr(code: str, request: Request, authorization: str | None = Header(default=None)):
    code = room_code(code)
    with store.room(code) as state:
        role, _ = identity(state, authorization)
        if role != "host":
            raise HTTPException(403, "Only the presenter can request the room QR code.")
        # Older rooms did not store a link; they continue to work after this upgrade.
        link = state.get("join_url") or join_link(request, code)
    return qr_payload(link)


@app.post("/api/rooms/{code}/join")
def join_room(code: str, body: JoinRoom):
    code = room_code(code)
    name = " ".join(body.nickname.split())
    if not name or any(ord(c) < 32 for c in name):
        raise HTTPException(400, "Choose a visible pseudonym, up to 24 characters.")
    with store.room(code) as state:
        settle(state)
        if state["phase"] == "finished":
            raise HTTPException(409, "This game has finished. Ask for a new room code.")
        if len(state["players"]) >= MAX_PLAYERS:
            raise HTTPException(409, "This room is full.")
        if any(p["nickname"].casefold() == name.casefold() for p in state["players"].values()):
            raise HTTPException(409, "That pseudonym is taken. Try another one.")
        pid, token = secrets.token_hex(8), secrets.token_urlsafe(32)
        state["players"][pid] = {"nickname": name, "token": digest(token), "score": 0, "streak": 0,
                                 "correct": 0, "history": [], "joined_at": time.time()}
    return {"code": code, "player_id": pid, "token": token}


def team_player(state, authorization):
    """Team membership changes share the same transaction lock as round start."""
    role, pid = identity(state, authorization)
    if role != "player":
        raise HTTPException(403, "Only players can create or join a team.")
    if "teams" not in state:
        raise HTTPException(409, "Create a new room to use teams.")
    if state["phase"] != "lobby":
        raise HTTPException(409, "Team selection is closed. Teams lock when the game starts.")
    return pid


@app.post("/api/rooms/{code}/teams")
def create_team(code: str, body: CreateTeam, authorization: str | None = Header(default=None)):
    name = " ".join(body.name.split())
    if not name or any(not c.isprintable() for c in name):
        raise HTTPException(400, "Choose a visible group name, up to 40 characters.")
    try:
        name.encode("utf-8")
    except UnicodeError as error:
        raise HTTPException(400, "Use valid Unicode in the group name.") from error
    with store.room(room_code(code)) as state:
        pid = team_player(state, authorization)
        player = state["players"][pid]
        current = state["teams"].get(player.get("team_id"))
        if current:
            # A retry after a lost response must not create a second team.
            if current["creator_id"] != pid or current["name"] != name:
                raise HTTPException(409, "You already belong to a team.")
        else:
            tid = secrets.token_hex(8)
            state["teams"][tid] = {"name": name, "creator_id": pid}
            player["team_id"] = tid
        return view(state, "player", pid)


@app.post("/api/rooms/{code}/teams/{team_id}/join")
def join_team(code: str, team_id: str, authorization: str | None = Header(default=None)):
    with store.room(room_code(code)) as state:
        pid = team_player(state, authorization)
        if team_id not in state["teams"]:
            raise HTTPException(404, "Team not found. Refresh the list and choose an existing team.")
        player = state["players"][pid]
        if player.get("team_id") and player["team_id"] != team_id:
            raise HTTPException(409, "You already belong to a team.")
        player["team_id"] = team_id
        return view(state, "player", pid)


@app.get("/api/rooms/{code}/state")
def get_state(code: str, authorization: str | None = Header(default=None)):
    with store.room(room_code(code)) as state:
        role, pid = identity(state, authorization)
        settle(state)
        return view(state, role, pid)


@app.post("/api/rooms/{code}/vote")
def vote(code: str, body: Vote, authorization: str | None = Header(default=None)):
    # Commit expiry before returning errors, so the timer always settles once.
    error = None
    with store.room(room_code(code)) as state:
        role, pid = identity(state, authorization)
        settle(state)
        if role != "player":
            error = (403, "The presenter cannot vote.")
        elif state["phase"] != "live" or body.round_index != state["index"]:
            error = (409, "Voting is closed for this round.")
        elif pid in state["votes"]:
            error = (409, "Your answer is already locked in.")
        else:
            state["votes"][pid] = {"answer": body.answer}
        result = view(state, role, pid)
    if error:
        raise HTTPException(*error)
    return result


@app.post("/api/rooms/{code}/control")
def control(code: str, body: Control, authorization: str | None = Header(default=None)):
    error = None
    with store.room(room_code(code)) as state:
        role, pid = identity(state, authorization)
        if role != "host":
            raise HTTPException(403, "Only the presenter can control rounds.")
        settle(state)
        if body.revision != state["revision"]:
            error = (409, "Game state changed. Try again with the updated screen.")
        elif body.action == "start" and state["phase"] in ("lobby", "ready"):
            if not state["players"]:
                error = (409, "Wait for at least one player to join.")
            else:
                state["duration"] = round_seconds(state)
                if state["rounds"][state["index"]]["kind"] == "video":
                    # Do not start voting while the clip is still playing.
                    # Only the presenter's completed-player event (or their
                    # explicit fallback button) can release the timer.
                    state["deadline"] = None
                    state["phase"] = "watching"
                else:
                    state["deadline"] = time.time() + state["duration"]
                    state["phase"] = "live"
                state["revision"] += 1
        elif body.action == "begin_voting" and state["phase"] == "watching" and state["rounds"][state["index"]]["kind"] == "video":
            # Server-authoritative countdown, starting AFTER the video ends.
            # The same revision guard prevents duplicate completion signals.
            state["deadline"] = time.time() + state["duration"]
            state["phase"] = "live"
            state["revision"] += 1
        elif body.action == "next" and state["phase"] == "revealed":
            if state["index"] == len(state["rounds"]) - 1:
                state["phase"] = "finished"
            else:
                state["index"] += 1
                state["votes"] = {}
                state.pop("team_results", None)
                state.pop("pool_deadline", None)
                state["duration"] = round_seconds(state)
                if state["rounds"][state["index"]]["kind"] == "video":
                    state["deadline"] = None
                    state["phase"] = "watching"
                else:
                    state["deadline"] = time.time() + state["duration"]
                    state["phase"] = "live"
            state["revision"] += 1
        else:
            error = (409, "That action is unavailable in this phase.")
        result = view(state, role, pid)
    if error:
        raise HTTPException(*error)
    return result




# The following editor is separate from the game interface and Mercato.
# It can be opened directly on the Vercel deployment without an extra login.
class SaveSharedDeck(BaseModel):
    revision: str = Field(max_length=80)
    rounds: list[dict] = Field(max_length=200)


def _allow_deck_request(request: Request):
    """Allow the standalone deck editor without a separate password.

    Writes still reject unexpected browser origins when an Origin header is
    provided. Mercato server-to-server calls omit Origin and remain allowed.
    """
    if request.method != 'GET':
        origin = request.headers.get('origin', '')
        if origin and origin != str(request.base_url).rstrip('/'):
            raise HTTPException(403, 'Editor request origin is not allowed.')


@app.get('/deck-manager')
def deck_manager_page():
    return FileResponse(ROOT / 'manager_assets' / 'index.html', headers={'Cache-Control': 'no-store'})


@app.get('/api/deck')
def global_get_deck(request: Request):
    _allow_deck_request(request)
    starter = load_rounds(ROOT, fallback=ROUNDS)
    result = get_shared_deck(store, starter)
    result.update({'warning': '', 'max_upload_mb': 4})
    return result


@app.get('/api/starter')
def global_starter_deck(request: Request):
    _allow_deck_request(request)
    return {'rounds': load_rounds(ROOT, fallback=ROUNDS), 'warning': ''}


@app.put('/api/deck')
def global_put_deck(body: SaveSharedDeck, request: Request):
    _allow_deck_request(request)
    try:
        rounds = validate_rounds(body.rounds, ROOT, require_media=True)
    except DeckError as error:
        raise HTTPException(422, str(error)) from error
    return put_shared_deck(store, load_rounds(ROOT, fallback=ROUNDS), body.revision, rounds)


@app.post('/api/deck/import-bundle')
async def global_import_bundle(request: Request, revision: str, mode: Literal['replace', 'append'] = 'replace',
                               acknowledge_media_rights: bool = False):
    """Import a validated ZIP atomically at the shared deck level.

    The ZIP is parsed and every question validated before writes. External
    sources are restricted to fixed, attributed publisher images; the caller
    explicitly acknowledges permission/rights before we retrieve those files.
    On failure, the saved deck stays untouched. Newly uploaded blobs can
    remain unused if a later database conflict occurs.
    """
    _allow_deck_request(request)
    if not request.headers.get('content-type', '').lower().startswith(('application/zip', 'application/octet-stream')):
        raise HTTPException(415, 'Choose a .zip file.')
    if len(revision) > 80:
        raise HTTPException(422, 'Invalid saved-deck revision.')
    if request.headers.get('content-length', '').isdigit() and int(request.headers['content-length']) > MAX_ZIP:
        raise HTTPException(413, 'Vercel accepts ZIP uploads up to 4 MB.')
    data = bytearray()
    async for chunk in request.stream():
        data.extend(chunk)
        if len(data) > MAX_ZIP:
            raise HTTPException(413, 'Vercel accepts ZIP uploads up to 4 MB.')
    bundle_rounds, manifest_media, embedded = read_bundle(bytes(data))
    if any(path not in embedded for path in manifest_media) and not acknowledge_media_rights:
        raise HTTPException(422, 'Confirm that you have permission to use the credited publisher photographs.')

    starter = load_rounds(ROOT, fallback=ROUNDS)
    current = get_shared_deck(store, starter)
    if revision != current['revision']:
        raise HTTPException(409, 'The shared deck changed in another editor. Reload before importing.')
    base = current['rounds'] if mode == 'append' else []
    if len(base) + len(bundle_rounds) > 200:
        raise HTTPException(422, 'The combined deck exceeds 200 questions.')

    token = os.getenv('BLOB_READ_WRITE_TOKEN', '')
    if manifest_media and not token:
        raise HTTPException(503, 'Connect a PUBLIC Blob store to the IceBreaker Vercel deployment (BLOB_READ_WRITE_TOKEN).')
    assets = collect_assets(manifest_media, embedded)
    urls = upload_assets(assets, token)
    try:
        merged = validate_rounds(base + substitute_assets(bundle_rounds, urls), ROOT, require_media=True)
    except DeckError as error:
        raise HTTPException(422, str(error)) from error
    saved = put_shared_deck(store, starter, revision, merged)
    saved.update({'imported_count': len(bundle_rounds), 'uploaded_images': len(urls), 'mode': mode,
                  'message': f'ZIP import completed: {len(bundle_rounds)} questions and {len(urls)} images. '
                             'The global deck and new rooms now use the saved version.'})
    return saved


@app.get('/api/media')
def global_list_media(request: Request):
    _allow_deck_request(request)
    result = {kind: [] for kind in MEDIA_FOLDERS}
    for kind, folder in MEDIA_FOLDERS.items():
        directory = ROOT / 'static' / folder
        for file in sorted(directory.iterdir()) if directory.is_dir() else []:
            if file.is_file() and file.suffix.lower() in MEDIA_EXTENSIONS[kind]:
                result[kind].append({'path': '/static/' + folder + '/' + file.name, 'name': file.name})
    token = os.getenv('BLOB_READ_WRITE_TOKEN', '')
    if token:
        try:
            from vercel.blob import BlobClient
            with BlobClient(token=token) as blob:
                for kind, folder in MEDIA_FOLDERS.items():
                    page = blob.list_objects(prefix='icebreaker/' + folder + '/', limit=100)
                    for item in page.blobs:
                        if is_public_icebreaker_blob(item.url, folder):
                            result[kind].append({'path': item.url, 'name': item.pathname.split('/')[-1]})
        except Exception:
            # Listing failure must not prevent a saved deck from being edited.
            pass
    return result


@app.post('/api/media')
async def global_upload_media(request: Request, kind: str, extension: str):
    _allow_deck_request(request)
    if kind not in MEDIA_FOLDERS or extension.lower() not in MEDIA_EXTENSIONS[kind]:
        raise HTTPException(422, 'Unsupported media format.')
    max_bytes = 4 * 1024 * 1024  # Vercel Function body limit; never pretend 25MB works here.
    if request.headers.get('content-length', '').isdigit() and int(request.headers['content-length']) > max_bytes:
        raise HTTPException(413, 'Vercel uploads are limited to 4 MB. Compress the file or upload it through Mercato.')
    chunks, size = [], 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > max_bytes:
            raise HTTPException(413, 'Vercel uploads are limited to 4 MB. Compress the file or upload it through Mercato.')
        chunks.append(chunk)
    if not size:
        raise HTTPException(422, 'Empty upload.')
    token = os.getenv('BLOB_READ_WRITE_TOKEN', '')
    if not token:
        raise HTTPException(503, 'Connect a PUBLIC Vercel Blob store to IceBreaker (BLOB_READ_WRITE_TOKEN).')
    name = 'icebreaker/' + MEDIA_FOLDERS[kind] + '/' + secrets.token_hex(16) + extension.lower()
    try:
        from vercel.blob import BlobClient
        with BlobClient(token=token) as blob:
            item = blob.put(name, b''.join(chunks), access='public',
                            content_type=mimetypes.guess_type(name)[0] or 'application/octet-stream',
                            add_random_suffix=True)
        url = item.get('url', '') if isinstance(item, dict) else getattr(item, 'url', '')
    except Exception as error:
        raise HTTPException(502, 'Vercel Blob upload failed. Check store access and token.') from error
    if not is_public_icebreaker_blob(url, MEDIA_FOLDERS[kind]):
        raise HTTPException(502, 'Vercel Blob did not return a valid public media URL.')
    return {'media': url, 'size': size, 'synced': True}


app.mount('/manager-assets', StaticFiles(directory=ROOT / 'manager_assets'), name='manager-assets')


app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
