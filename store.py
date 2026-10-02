"""One transaction/row lock per room keeps votes and reveals atomic across workers."""
import json
import os
import sqlite3
import time
from contextlib import closing, contextmanager
from pathlib import Path

from fastapi import HTTPException


class Store:
    def __init__(self):
        self.url = os.getenv("DATABASE_URL", "").strip()
        self.path = Path(os.getenv("SQLITE_PATH", "game.sqlite3"))

    def payload(self, state):
        if self.url:
            from psycopg.types.json import Jsonb
            return Jsonb(state)
        return json.dumps(state)

    def connect(self):
        if self.url:
            import psycopg
            # Supabase transaction pooler does not support prepared statements.
            return psycopg.connect(self.url, prepare_threshold=None,
                                   connect_timeout=10, sslmode="require")
        if os.getenv("VERCEL"):
            raise HTTPException(503, "Set DATABASE_URL in Vercel before creating a game.")
        connection = sqlite3.connect(self.path, timeout=15)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("CREATE TABLE IF NOT EXISTS rooms "
                           "(code TEXT PRIMARY KEY, expires_at REAL NOT NULL, state TEXT NOT NULL)")
        connection.commit()
        return connection

    def create(self, code, state):
        with closing(self.connect()) as connection:
            table = "icebreaker.rooms" if self.url else "rooms"
            mark = "%s" if self.url else "?"
            # Expired rooms become inaccessible even if no scheduled cleanup runs.
            connection.execute(f"DELETE FROM {table} WHERE expires_at < {mark}", (time.time(),))
            try:
                connection.execute(
                    f"INSERT INTO {table} (code, expires_at, state) VALUES ({mark}, {mark}, {mark})",
                    (code, state["expires_at"], self.payload(state)))
            except Exception as error:
                if isinstance(error, sqlite3.IntegrityError) or getattr(error, "sqlstate", None) == "23505":
                    return False
                raise
            connection.commit()
            return True

    @contextmanager
    def room(self, code):
        connection = self.connect()
        try:
            table = "icebreaker.rooms" if self.url else "rooms"
            mark = "%s" if self.url else "?"
            if not self.url:
                connection.execute("BEGIN IMMEDIATE")
            lock = " FOR UPDATE" if self.url else ""
            row = connection.execute(
                f"SELECT state FROM {table} WHERE code={mark}{lock}", (code,)).fetchone()
            if not row:
                raise HTTPException(404, "Room not found. Check the six-character code.")
            state = row[0] if isinstance(row[0], dict) else json.loads(row[0])
            if state["expires_at"] <= time.time():
                raise HTTPException(410, "This room has expired. Ask the presenter for a new code.")
            before = json.dumps(state, sort_keys=True)
            yield state
            after = json.dumps(state, sort_keys=True)
            if before != after:
                connection.execute(f"UPDATE {table} SET state={mark} WHERE code={mark}", (self.payload(state), code))
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()
