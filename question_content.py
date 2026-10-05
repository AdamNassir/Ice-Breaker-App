"""Shared deck format. questions.json takes priority; Content.py is the starter deck."""
import copy
import json
import re
from pathlib import Path, PurePosixPath
from typing import Literal
from urllib.parse import urlsplit, parse_qs

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

ROOT = Path(__file__).resolve().parent
DECK_FILE = "questions.json"
MAX_DECK_BYTES = 2 * 1024 * 1024
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif", ".bmp"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".opus", ".flac", ".m4a", ".aac", ".webm"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".ogv", ".mov", ".m4v"}
MEDIA_FOLDERS = {"image": "images", "audio": "audio", "video": "videos"}
MEDIA_EXTENSIONS = {"image": IMAGE_EXTENSIONS, "audio": AUDIO_EXTENSIONS, "video": VIDEO_EXTENSIONS}


# These two bundled articles predate text_style; old room snapshots may contain
# the parser's former default "plain". Limit migration to those known titles
# and headlines so custom plain text remains an explicit author choice.
LEGACY_NEWS_HEADLINES = {
    "A very expensive refresh": "Bitcoin falls 50% after exchange dashboard repeats a decimal error",
    "The trophy before the ceremony": "Ballon d’Or result briefly appears in trophy delivery tracker",
}


def text_presentation(question):
    if question.get("kind") != "text":
        return "plain"
    selected = question.get("text_style")
    if selected == "news":
        return "news"
    title = str(question.get("title", "")).strip()
    headline = str(question.get("body", "")).split("\n", 1)[0].strip()
    if title in LEGACY_NEWS_HEADLINES and headline == LEGACY_NEWS_HEADLINES[title]:
        return "news"
    if selected is None and title.startswith("News Article About "):
        return "news"
    return "plain"


def youtube_id(value):
    parsed = urlsplit(value)
    host = parsed.hostname
    if host == "youtu.be":
        identifier = parsed.path.strip('/')
    elif host in {"youtube.com", "www.youtube.com", "m.youtube.com", "www.youtube-nocookie.com"}:
        if parsed.path == '/watch':
            identifier = parse_qs(parsed.query).get('v', [''])[0]
        elif parsed.path.startswith(('/embed/', '/shorts/')):
            identifier = parsed.path.split('/')[2]
        else:
            return None
    else:
        return None
    return identifier if re.fullmatch(r'[A-Za-z0-9_-]{11}', identifier) else None


class DeckError(ValueError):
    pass


class ImageHighlight(BaseModel):
    """Circle position and radius as percentages of the original image width."""
    model_config = ConfigDict(extra="forbid")
    x: float = Field(ge=0, le=100)
    y: float = Field(ge=0, le=100)
    radius: float = Field(gt=0, le=100)


class RevealSource(BaseModel):
    """An explicitly configured source credit, public only after reveal."""
    model_config = ConfigDict(extra="forbid")
    label: str = Field(min_length=1, max_length=300)
    url: str = Field(min_length=1, max_length=2000)

    @model_validator(mode="after")
    def source_valid(self):
        self.label = self.label.strip()
        self.url = self.url.strip()
        if not self.label or '\x00' in self.label:
            raise ValueError("Give each reveal source a readable label.")
        for value in (self.label, self.url):
            try:
                value.encode('utf-8')
            except UnicodeError as error:
                raise ValueError("Use valid Unicode in reveal sources.") from error
        parsed = urlsplit(self.url)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("Reveal source links must be full https:// URLs without credentials.")
        return self


class Question(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=120)
    kind: Literal["text", "code", "commit", "image", "audio", "video"]
    answer: Literal["AI", "HUMAN"]
    body: str = Field(default="", max_length=50000)
    context: str = Field(default="", max_length=2000)
    text_style: Literal["plain", "news"] = "plain"
    seconds: int | None = Field(default=None, ge=5, le=120, strict=True)
    difficulty: int | None = Field(default=None, ge=1, le=5, strict=True)
    media: str = Field(default="", max_length=300)
    media_url: str = Field(default="", max_length=2000)
    media_start: int | None = Field(default=None, ge=0, le=7200, strict=True)
    media_end: int | None = Field(default=None, ge=1, le=7200, strict=True)
    alt: str = Field(default="", max_length=1000)
    image_fit: Literal["contain", "cover"] = "contain"
    image_position: str = Field(default="center", max_length=60)
    image_reveal: str = Field(default="", max_length=1800)
    image_highlight: ImageHighlight | None = None
    reveal_sources: list[RevealSource] = Field(default_factory=list, max_length=8)
    explanation: str = Field(default="", max_length=6000)
    technical_note: str = Field(default="", max_length=6000)
    discussion: str = Field(default="", max_length=2000)
    source: str = Field(default="", max_length=3000)
    source_url: str = Field(default="", max_length=2000)
    technical_source_url: str = Field(default="", max_length=2000)

    @model_validator(mode="before")
    @classmethod
    def legacy_news_layout(cls, value):
        if isinstance(value, dict) and text_presentation(value) == "news":
            value = {**value, "text_style": "news"}
        return value

    @model_validator(mode="after")
    def content_valid(self):
        for name in type(self).model_fields:
            value = getattr(self, name)
            if isinstance(value, str):
                if '\x00' in value:
                    raise ValueError("Remove null characters from the question text.")
                try:
                    value.encode('utf-8')
                except UnicodeError as error:
                    raise ValueError("Use valid Unicode text in the question fields.") from error
        self.title = self.title.strip()
        self.source_url = self.source_url.strip()
        self.media_url = self.media_url.strip()
        self.technical_source_url = self.technical_source_url.strip()
        if not self.title:
            raise ValueError("Give the question a title.")
        if self.kind in {"text", "code", "commit"} and not self.body.strip():
            raise ValueError("Enter the question text or code.")
        if self.kind in MEDIA_FOLDERS:
            if self.media and self.media_url:
                raise ValueError("Choose either an uploaded file or an online link, not both.")
            if self.media_end is not None and self.media_end <= (self.media_start or 0):
                raise ValueError("Clip end must be after clip start (seconds from the beginning).")
        if self.media_url:
            if self.kind not in {"audio", "video"}:
                raise ValueError("Online links are supported for audio and video; upload images locally.")
            parsed = urlsplit(self.media_url)
            if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
                raise ValueError("Media links must be full https:// URLs without credentials.")
            if not (self.kind == 'video' and youtube_id(self.media_url)):
                if PurePosixPath(parsed.path).suffix.lower() not in MEDIA_EXTENSIONS[self.kind]:
                    raise ValueError("Use a direct audio/video file URL, or a YouTube watch/share link for video.")
        elif self.kind in MEDIA_FOLDERS:
            expected = MEDIA_FOLDERS[self.kind]
            path = PurePosixPath(self.media)
            if (not self.media.startswith(f"/static/{expected}/") or ".." in path.parts or
                    "\\" in self.media or "%" in self.media or "?" in self.media or "#" in self.media):
                raise ValueError(f"Choose a file from static/{expected} or upload one.")
            extensions = MEDIA_EXTENSIONS[self.kind]
            if path.suffix.lower() not in extensions:
                raise ValueError("This media format is not supported. Choose a browser-compatible file.")
        for value in (self.source_url, self.technical_source_url):
            if value:
                parsed = urlsplit(value)
                if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
                    raise ValueError("Reference links must be full https:// URLs without credentials.")
        return self


def validate_rounds(rounds, root=ROOT, allow_empty=False, *, require_media=True):
    if not isinstance(rounds, list):
        raise DeckError("The deck must contain a list of questions.")
    if not rounds and not allow_empty:
        raise DeckError("Add at least one question before saving the deck.")
    if len(rounds) > 200:
        raise DeckError("A deck can contain up to 200 questions.")
    result = []
    for index, row in enumerate(rounds, 1):
        try:
            question = Question.model_validate(row)
        except ValidationError as error:
            first = error.errors()[0]
            field = ".".join(str(p) for p in first["loc"])
            message = first["msg"].removeprefix("Value error, ")
            raise DeckError(f"Question {index}{' (' + field + ')' if field else ''}: {message}") from error
        if question.kind in MEDIA_FOLDERS and not question.media_url:
            base = (Path(root) / "static" / MEDIA_FOLDERS[question.kind]).resolve()
            media = (Path(root) / question.media.lstrip("/")).resolve()
            if not media.is_relative_to(base):
                raise DeckError(f"Question {index}: media must stay inside static/{base.name}.")
            if require_media and not media.is_file():
                raise DeckError(f"Question {index}: the selected media file is missing ({question.media}). Upload a replacement or remove this question.")
        result.append(question.model_dump(exclude_none=True))
    return result


def deck_bytes(rounds):
    data = (json.dumps({"schema_version": 1, "rounds": rounds}, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if len(data) > MAX_DECK_BYTES:
        raise DeckError("The deck is too large (maximum 2 MB of question text). Media files are stored separately.")
    return data


def parse_deck(data, root=ROOT, allow_empty=False, *, require_media=True):
    if len(data) > MAX_DECK_BYTES:
        raise DeckError("The question file is too large (maximum 2 MB).")
    try:
        value = json.loads(data)
    except (ValueError, UnicodeError) as error:
        raise DeckError("The question file is not valid UTF-8 JSON.") from error
    if isinstance(value, dict):
        if value.get("schema_version", 1) != 1:
            raise DeckError("This question file uses an unsupported format version.")
        value = value.get("rounds")
    return validate_rounds(value, root, allow_empty, require_media=require_media)


def load_rounds(root=ROOT, fallback=None):
    path = Path(root) / DECK_FILE
    if path.exists():
        try:
            # Limit the read even if the file was edited outside the manager.
            with path.open("rb") as file:
                data = file.read(MAX_DECK_BYTES + 1)
        except OSError as error:
            raise DeckError("Could not read questions.json.") from error
        return parse_deck(data, root)
    if fallback is None:
        from Content import ROUNDS
        fallback = ROUNDS
    return validate_rounds(copy.deepcopy(fallback), root)
