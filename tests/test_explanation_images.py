"""Reveal-only explanation images: validation, import and private-vs-reveal game API."""
import io
import json
import os
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

import main
from store import Store
from question_content import DeckError, validate_rounds
from deck_bundle_import import read_bundle, substitute_assets

SAMPLE = {'title':'Who wrote this?', 'kind':'text','answer':'AI',
          'body':'A short story that looks human.', 'explanation':'This was generated using AI.',
          'explanation_image':'/static/images/sample19.png',
          'explanation_image_alt':'Example image of the generation process.'}


def test_explanation_image_valid_for_any_type_and_rejects_untrusted_urls():
    for kind, rest in (
        ('text',{'body':'Some writing'}),
        ('video',{'media_url':'https://www.youtube.com/watch?v=9SWEA2y2DjQ'}),
        ('image',{'media':'/static/images/sample19.png'})):
        row={**SAMPLE, 'kind':kind, **rest}
        saved=validate_rounds([row],require_media=True)[0]
        assert saved['explanation_image']==SAMPLE['explanation_image']
    for bad in ('https://untrusted.example/photo.jpg', '/static/images/../../etc/secret.jpg',
                '/static/videos/movie.mp4'):
        with pytest.raises(DeckError):
            validate_rounds([{**SAMPLE,'explanation_image':bad}],require_media=False)


def test_explanation_image_hidden_until_answer_is_revealed():
    with tempfile.TemporaryDirectory() as folder:
        game_store=Store();game_store.url='';game_store.path=Path(folder)/'rooms.sqlite'
        with patch.object(main,'store',game_store),patch.dict(os.environ,{'PRESENTER_PASSWORD':'','VERCEL':''}):
            client=TestClient(main.app)
            room=client.post('/api/rooms',json={'seconds':5,'deck':[SAMPLE]})
            assert room.status_code==200,room.text
            code=room.json()['code'];host={'Authorization':'Bearer '+room.json()['token']}
            join=client.post(f'/api/rooms/{code}/join',json={'nickname':'Participant'})
            assert join.status_code==200,join.text
            player={'Authorization':'Bearer '+join.json()['token']}
            started=client.post(f'/api/rooms/{code}/control',headers=host,json={'action':'start','revision':0})
            assert started.status_code==200,started.text
            for who in (host,player):
                before=client.get(f'/api/rooms/{code}/state',headers=who).json()
                assert before['phase']=='live'
                assert before['reveal'] is None
                assert 'explanation_image' not in before['question']
                assert SAMPLE['explanation'] not in json.dumps(before['question'])
            with game_store.room(code) as state:
                state['deadline']=0
            for who in (host,player):
                after=client.get(f'/api/rooms/{code}/state',headers=who).json()
                assert after['phase']=='revealed'
                assert after['reveal']['explanation_image']==SAMPLE['explanation_image']
                assert after['reveal']['explanation_image_alt']==SAMPLE['explanation_image_alt']
                assert after['reveal']['explanation']==SAMPLE['explanation']


def test_zip_import_resolves_embedded_explanation_image():
    photo=io.BytesIO();Image.new('RGB',(1200,900),'white').save(photo,format='JPEG')
    row={**SAMPLE,'explanation_image':'assets/explanation.jpg'}
    content=io.BytesIO()
    with zipfile.ZipFile(content,'w',zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr('manifest.json',json.dumps({'format':'icebreaker-deck-bundle','version':1,
                                                   'media':{'assets/explanation.jpg':{}}}))
        bundle.writestr('questions.json',json.dumps({'schema_version':1,'rounds':[row]}))
        bundle.writestr('assets/explanation.jpg',photo.getvalue())
    rounds,manifest,embedded=read_bundle(content.getvalue())
    assert set(manifest)=={'assets/explanation.jpg'}
    assert set(embedded)==set(manifest)
    replaced=substitute_assets(rounds,{'assets/explanation.jpg':'https://test.public.blob.vercel-storage.com/icebreaker/images/answer.jpg'})
    assert replaced[0]['explanation_image'].endswith('/answer.jpg')
    assert validate_rounds(replaced)[0]['explanation_image']==replaced[0]['explanation_image']
