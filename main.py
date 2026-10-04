"""FastAPI entrypoint: python -m uvicorn main:app --reload"""
import copy
import base64
import hashlib
import os
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
from question_content import DeckError, load_rounds
from store import Store

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


class JoinRoom(BaseModel):
    nickname: str = Field(min_length=1, max_length=24)


class Vote(BaseModel):
    answer: Literal["AI", "HUMAN"]
    round_index: int = Field(ge=0)


class Control(BaseModel):
    action: Literal["start", "next"]
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


def settle(state):
    """Reveal only after the server deadline. A phase change makes this exactly-once."""
    now = time.time()
    if state["phase"] != "live" or now < state["deadline"]:
        return
    answer = state["rounds"][state["index"]]["answer"]
    for player_id, player in state["players"].items():
        # Late joiners who joined after the deadline don't lose a streak.
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
    result = {"code": state["code"], "title": state["title"], "phase": state["phase"],
              "round_index": state["index"], "round_number": state["index"] + 1,
              "round_count": len(state["rounds"]), "revision": state["revision"],
              "server_time": time.time(), "deadline": state["deadline"],
              "duration": state["duration"], "player_count": len(players),
              "answered_count": len(state["votes"]), "leaderboard": board, "question": None,
              "me": None, "reveal": None}
    if state["phase"] in ("live", "revealed"):
        question = state["rounds"][state["index"]]
        result["question"] = {k: question[k] for k in
                              ("title", "kind", "body", "media", "alt", "image_fit", "image_position",
                               "media_url", "media_start", "media_end", "difficulty", "context") if k in question}
        if state["phase"] == "revealed":
            result["reveal"] = {k: question[k] for k in
                                ("answer", "explanation", "source", "source_url", "technical_note",
                                 "discussion", "technical_source_url") if k in question}
            result["reveal"]["distribution"] = {
                choice: sum(v["answer"] == choice for v in state["votes"].values()) for choice in ("AI", "HUMAN")}
    if player_id:
        player = state["players"][player_id]
        result["me"] = {**next(row for row in board if row["id"] == player_id),
                        "vote": state["votes"].get(player_id, {}).get("answer"),
                        "history": player["history"]}
    return result


@app.middleware("http")
async def response_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    if request.url.path.startswith("/api/"):
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


@app.get("/api/health")
def health():
    with closing(store.connect()) as connection:
        connection.execute("SELECT 1")
        # Check that the migration and grants are actually ready, without changing data.
        if store.url:
            connection.execute("SELECT code FROM icebreaker.rooms LIMIT 0")
    return {"status": "ok", "storage": "Supabase PostgreSQL" if store.url else "local SQLite"}


@app.post("/api/rooms")
def create_room(body: CreateRoom, request: Request):
    password = os.getenv("PRESENTER_PASSWORD", "")
    if os.getenv("VERCEL") and not password:
        raise HTTPException(503, "Set PRESENTER_PASSWORD in Vercel before creating a game.")
    if password and not secrets.compare_digest(body.password.encode(), password.encode()):
        raise HTTPException(403, "Presenter password is incorrect.")
    try:
        rounds = load_rounds(ROOT, fallback=ROUNDS)
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
                 "deadline": None, "duration": body.seconds, "default_seconds": body.seconds, "votes": {}}
        if store.create(code, state):
            return {"code": code, "token": token, "join_url": state["join_url"]}
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
                state["duration"] = max(5, min(120, int(state["rounds"][state["index"]].get("seconds", state["default_seconds"]))))
                state["deadline"] = time.time() + state["duration"]
                state["phase"] = "live"
                state["revision"] += 1
        elif body.action == "next" and state["phase"] == "revealed":
            if state["index"] == len(state["rounds"]) - 1:
                state["phase"] = "finished"
            else:
                state["index"] += 1
                state["phase"] = "ready"
                state["votes"] = {}
                state["deadline"] = None
            state["revision"] += 1
        else:
            error = (409, "That action is unavailable in this phase.")
        result = view(state, role, pid)
    if error:
        raise HTTPException(*error)
    return result


app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
