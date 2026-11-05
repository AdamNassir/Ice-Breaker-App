"""Open global editor, persistence, concurrency and new-room behavior."""
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

import main
from question_content import DeckError, validate_rounds
from store import Store


STARTER_BITCOIN = next(q for q in main.ROUNDS if q['kind'] == 'text' and 'bitcoin' in q['body'].lower())
SAMPLE = {'title': 'Cloud updated article', 'kind': 'text', 'text_style': 'news',
          'body': 'A news headline\n\nLead paragraph\n\nDetailed story here.', 'answer': 'AI',
          'news': {'publication': 'The Example Daily', 'author': 'Demo Writer',
                   'published': '3 November 2026', 'section': 'Economy',
                   'headline': 'A different headline', 'hero_image': '',
                   'related': [{'section': 'Technology', 'title': 'Sample article', 'image': 'ai'}]}}


def test_global_deck_open_editor_preserves_legacy_starter():
    with tempfile.TemporaryDirectory() as temp:
        state = Store()
        state.url = ''
        state.path = Path(temp) / 'room.sqlite3'
        with patch.object(main, 'store', state), patch.dict(os.environ, {'DATABASE_URL':'', 'PRESENTER_PASSWORD':'presenter-demo'}):
            client = TestClient(main.app)
            assert client.get('/deck-manager').status_code == 200
            assert client.get('/api/deck').status_code == 200
            snapshot = client.get('/api/deck').json()
            assert snapshot['initialized'] is False
            assert any('bitcoin' in q['body'].lower() for q in snapshot['rounds'])
            created = client.put('/api/deck', json={'revision':snapshot['revision'], 'rounds':[SAMPLE]})
            assert created.status_code == 200, created.text
            assert created.json()['initialized'] is True
            assert client.put('/api/deck', json={'revision':snapshot['revision'], 'rounds':[SAMPLE]}).status_code == 409
            assert client.get('/api/deck').json()['rounds'][0]['news']['author'] == 'Demo Writer'
            # No need to run Mercato or redeploy to make a new room use the shared deck.
            room = client.post('/api/rooms', json={'password':'presenter-demo'}).json()
            with state.room(room['code']) as saved:
                assert saved['rounds'][0]['title'] == 'Cloud updated article'
                assert saved['rounds'][0]['news']['publication'] == 'The Example Daily'
            current = client.get('/api/deck').json()
            invalid = dict(SAMPLE)
            invalid['news'] = {**SAMPLE['news'], 'hero_image':'https://attacker.example/img.jpg'}
            assert client.put('/api/deck', json={'revision':current['revision'], 'rounds':[invalid]}).status_code == 422
            # This project deliberately has no additional deck password.
            assert client.get('/manager-assets/app.js').status_code == 200
            assert client.get('/api/starter').status_code == 200


def test_news_fields_are_validated_and_serialized():
    rounds = validate_rounds([SAMPLE], require_media=False)
    assert rounds[0]['news']['headline'] == 'A different headline'
    assert rounds[0]['news']['related'][0]['title'] == 'Sample article'
    with __import__('pytest').raises(DeckError):
        validate_rounds([{**SAMPLE, 'news':{**SAMPLE['news'], 'related':[{'title':'bad','image':'javascript:alert(1)'}]}}], require_media=False)
