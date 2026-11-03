"""Canonical, revision-checked question deck persisted with the game database.

No filesystem writes on Vercel. PostgreSQL table is provisioned by
supabase_deck_migration.sql; SQLite is automatically provisioned for development.
"""
import hashlib
import json
import sqlite3
from contextlib import closing

from fastapi import HTTPException
from question_content import deck_bytes


def revision_for(rounds):
    return hashlib.sha256(deck_bytes(rounds)).hexdigest()


def get_shared_deck(store, starter):
    with closing(store.connect()) as db:
        if not store.url:
            db.execute('CREATE TABLE IF NOT EXISTS shared_decks (id INTEGER PRIMARY KEY, revision TEXT NOT NULL, state TEXT NOT NULL)')
            db.commit()
        try:
            row = db.execute('SELECT revision, state FROM icebreaker.shared_decks WHERE id=1' if store.url else
                             'SELECT revision, state FROM shared_decks WHERE id=1').fetchone()
        except Exception as error:
            raise HTTPException(503, 'Shared deck table missing. Run supabase_deck_migration.sql in Supabase SQL Editor.') from error
    if row:
        return {'rounds': row[1] if isinstance(row[1], list) else json.loads(row[1]),
                'revision': row[0], 'initialized': True, 'source': 'Shared Vercel deck'}
    return {'rounds': starter, 'revision': 'starter-' + revision_for(starter),
            'initialized': False, 'source': 'Bundled Bitcoin starter deck'}


def put_shared_deck(store, starter, expected_revision, rounds):
    new_rev = revision_for(rounds)
    with closing(store.connect()) as db:
        try:
            if not store.url:
                db.execute('CREATE TABLE IF NOT EXISTS shared_decks (id INTEGER PRIMARY KEY, revision TEXT NOT NULL, state TEXT NOT NULL)')
                db.execute('BEGIN IMMEDIATE')
            sql = 'SELECT revision, state FROM icebreaker.shared_decks WHERE id=1 FOR UPDATE' if store.url else 'SELECT revision, state FROM shared_decks WHERE id=1'
            row = db.execute(sql).fetchone()
            previous_rev = row[0] if row else 'starter-' + revision_for(starter)
            if expected_revision != previous_rev:
                db.rollback()
                raise HTTPException(409, 'The shared deck changed in another editor. Export your draft, reload, then merge your changes.')
            if store.url:
                from psycopg.types.json import Jsonb
                if row:
                    db.execute('UPDATE icebreaker.shared_decks SET revision=%s, state=%s, updated_at=now() WHERE id=1', (new_rev, Jsonb(rounds)))
                else:
                    db.execute('INSERT INTO icebreaker.shared_decks (id, revision, state) VALUES (1,%s,%s)', (new_rev, Jsonb(rounds)))
            else:
                if row:
                    db.execute('UPDATE shared_decks SET revision=?, state=? WHERE id=1', (new_rev, json.dumps(rounds)))
                else:
                    db.execute('INSERT INTO shared_decks (id, revision, state) VALUES (1,?,?)', (new_rev, json.dumps(rounds)))
            db.commit()
        except HTTPException:
            raise
        except Exception as error:
            db.rollback()
            raise HTTPException(503, 'Could not save shared deck. Verify database migration and grants.') from error
    return {'rounds': rounds, 'revision': new_rev, 'initialized': True, 'source': 'Shared Vercel deck',
            'message': 'Shared deck saved. Both editors and all NEW rooms now use this version.'}
