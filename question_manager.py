"""Local question editor. Run: python question_manager.py (not main:app)."""
import argparse
import hashlib
import os
import secrets
import threading
import time
import webbrowser
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from starlette.middleware.trustedhost import TrustedHostMiddleware

from Content import ROUNDS
from question_content import (AUDIO_EXTENSIONS, DECK_FILE, IMAGE_EXTENSIONS, MAX_DECK_BYTES,
                              ROOT, DeckError, deck_bytes, parse_deck, validate_rounds)

MAX_UPLOAD_BYTES = 25 * 1024 * 1024


class SaveDeck(BaseModel):
    model_config = ConfigDict(extra="forbid")
    revision: str = Field(max_length=80)
    rounds: list = Field(max_length=200)


def create_manager(root=ROOT, starter=None):
    root = Path(root).resolve()
    starter = ROUNDS if starter is None else starter
    manager = FastAPI(title="Local question manager", docs_url=None, redoc_url=None, openapi_url=None)
    manager.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])
    token = secrets.token_urlsafe(32)
    lock = threading.RLock()

    @manager.middleware("http")
    async def local_editor(request: Request, call_next):
        if os.getenv("VERCEL"):
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=403, content={"detail": "The question manager runs locally only."})
        if request.method in {"POST", "PUT", "DELETE", "PATCH"}:
            given = request.headers.get("X-Manager-Token", "")
            origin = request.headers.get("origin")
            if (not secrets.compare_digest(token.encode(), given.encode()) or
                    (origin and origin != f"{request.url.scheme}://{request.headers.get('host', '')}")):
                from fastapi.responses import JSONResponse
                return JSONResponse(status_code=403, content={"detail": "Refresh the local manager page and try again."})
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    def current():
        path = root / DECK_FILE
        if path.exists():
            if path.stat().st_size > MAX_DECK_BYTES:
                raise DeckError("questions.json exceeds 2 MB. Move it aside or restore a smaller backup before opening the manager.")
            with path.open("rb") as file:
                data = file.read(MAX_DECK_BYTES + 1)
            revision = hashlib.sha256(data).hexdigest()
            try:
                rounds = parse_deck(data, root, allow_empty=True)
                return rounds, revision, data, "questions.json", ""
            except DeckError as error:
                # Allow repairing a broken external edit, while preserving its backup.
                return [], revision, data, "questions.json", str(error)
        rounds = validate_rounds(starter, root, allow_empty=True)
        data = deck_bytes(rounds)
        return rounds, "starter-" + hashlib.sha256(data).hexdigest(), data, "Content.py starter deck", ""

    @manager.get("/")
    def editor():
        return FileResponse(ROOT / "manager_assets/index.html")

    @manager.get("/api/deck")
    def get_deck():
        with lock:
            try:
                rounds, revision, _, source, warning = current()
            except DeckError as error:
                raise HTTPException(503, str(error)) from error
            except OSError as error:
                raise HTTPException(503, "Cannot read the deck. Check files and access to the app folder.") from error
        return {"rounds": rounds, "revision": revision, "source": source, "warning": warning,
                "manager_token": token, "max_upload_mb": 25}

    @manager.get("/api/starter")
    def get_starter():
        try:
            return {"rounds": validate_rounds(starter, root, allow_empty=True)}
        except DeckError as error:
            raise HTTPException(400, str(error)) from error

    @manager.put("/api/deck")
    def save_deck(body: SaveDeck):
        try:
            rounds = validate_rounds(body.rounds, root)
            data = deck_bytes(rounds)
        except DeckError as error:
            raise HTTPException(400, str(error)) from error
        with lock:
            temp = None
            try:
                _, revision, previous, _, _ = current()
                if body.revision != revision:
                    raise HTTPException(409, "The saved deck changed in another tab or editor. Download your draft, reload the saved deck, and merge your changes.")
                backups = root / ".question-manager-backups"
                backups.mkdir(exist_ok=True)
                stamp = time.strftime("%Y%m%d-%H%M%S") + "-" + secrets.token_hex(3)
                (backups / f"questions-{stamp}.json").write_bytes(previous)
                temp = root / f".questions-{secrets.token_hex(8)}.tmp"
                with temp.open("xb") as file:
                    file.write(data)
                    file.flush()
                    os.fsync(file.fileno())
                os.replace(temp, root / DECK_FILE)
            except DeckError as error:
                raise HTTPException(400, str(error)) from error
            except OSError as error:
                raise HTTPException(503, "Could not save the deck. Check write access to the app folder.") from error
            finally:
                if temp is not None:
                    temp.unlink(missing_ok=True)
        return {"rounds": rounds, "revision": hashlib.sha256(data).hexdigest(),
                "source": "questions.json", "message": "Deck saved. Create a new local room, or commit the deck and media files and redeploy for Vercel."}

    @manager.get("/api/media")
    def list_media():
        result = {"image": [], "audio": []}
        for kind, folder, extensions in (("image", "images", IMAGE_EXTENSIONS), ("audio", "audio", AUDIO_EXTENSIONS)):
            directory = root / "static" / folder
            if directory.exists():
                for file in sorted(directory.iterdir()):
                    if file.is_file() and not file.is_symlink() and file.suffix.lower() in extensions:
                        result[kind].append({"path": f"/static/{folder}/{file.name}", "name": file.name})
        return result

    @manager.post("/api/media")
    async def upload(request: Request, kind: str, extension: str):
        extensions = IMAGE_EXTENSIONS if kind == "image" else AUDIO_EXTENSIONS if kind == "audio" else set()
        extension = extension.lower()
        if extension not in extensions:
            raise HTTPException(400, "Choose a supported image or audio file. See the format list beside the upload field.")
        length = request.headers.get("content-length", "")
        if length.isdigit() and int(length) > MAX_UPLOAD_BYTES:
            raise HTTPException(413, "This file exceeds 25 MB. Use a smaller copy.")
        directory = root / "static" / ("images" if kind == "image" else "audio")
        name = "sample_" + secrets.token_hex(12) + extension
        path = directory / name
        complete = False
        try:
            directory.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as file:
                size = 0
                async for chunk in request.stream():
                    size += len(chunk)
                    if size > MAX_UPLOAD_BYTES:
                        raise HTTPException(413, "This file exceeds 25 MB. Use a smaller copy.")
                    file.write(chunk)
            if size == 0:
                raise HTTPException(400, "The selected file is empty.")
            complete = True
        except OSError as error:
            raise HTTPException(503, "Could not copy this file. Check write access to the media folder.") from error
        finally:
            if not complete:
                path.unlink(missing_ok=True)
        return {"media": f"/static/{directory.name}/{name}", "size": size}

    manager.mount("/manager-assets", StaticFiles(directory=ROOT / "manager_assets"), name="manager-assets")
    manager.mount("/static", StaticFiles(directory=root / "static"), name="media")
    return manager


manager_app = create_manager()


def run():
    if os.getenv("VERCEL"):
        raise SystemExit("Run the question manager on your own computer, not Vercel.")
    parser = argparse.ArgumentParser(description="Edit questions locally and save them for the game.")
    parser.add_argument("--port", type=int, default=8765, help="Local port (default: 8765)")
    parser.add_argument("--no-browser", action="store_true", help="Print the link without opening a browser")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("Choose a port between 1 and 65535.")
    url = f"http://127.0.0.1:{args.port}"
    print(f"\nQuestion manager: {url}\nSaved questions and media stay in this app folder. Press Ctrl+C to stop.\n")
    if not args.no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    import uvicorn
    uvicorn.run(manager_app, host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    run()
