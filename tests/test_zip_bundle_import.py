"""Integration tests for ZIP-to-Vercel global-deck import; no live network calls."""
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
from deck_bundle_import import read_bundle, normalize_image
from store import Store

BUNDLE=Path('/mnt/data/IceBreaker_6_Questions_OneClick_Bundle.zip')


def sample_zip():
    return BUNDLE.read_bytes()


def tiny_jpeg():
    out=io.BytesIO()
    Image.new('RGB',(500,300),'white').save(out,'JPEG')
    return out.getvalue()


def test_six_question_bundle_manifest_is_complete():
    rounds,media,embedded=read_bundle(sample_zip())
    assert len(rounds)==6
    assert len(media)==5
    assert not embedded
    assert rounds[3]['media']=='assets/04_excel_world_championship_wide.jpg'
    assert media[rounds[3]['media']]['source_id']=='excel_arena_microsoft_2025'
    assert rounds[5]['image_fit']=='contain'
    assert rounds[2]['answer']=='AI'


def test_zip_import_replace_append_and_revision_reject(monkeypatch):
    with tempfile.TemporaryDirectory() as folder:
        store=Store()
        store.url=''
        store.path=Path(folder)/'test.sqlite'
        with patch.object(main,'store',store),patch.dict(os.environ,{'DECK_ADMIN_PASSWORD':'', 'BLOB_READ_WRITE_TOKEN':'test-not-real'}), \
             patch.object(main,'collect_assets',return_value={name:tiny_jpeg() for name in read_bundle(sample_zip())[1]}), \
             patch.object(main,'upload_assets',side_effect=lambda assets, token: {key:'https://valid.public.blob.vercel-storage.com/icebreaker/images/'+str(i)+'.jpg' for i,key in enumerate(assets)}):
            client=TestClient(main.app)
            previous=client.get('/api/deck').json()
            assert previous['initialized'] is False
            params={'revision':previous['revision'],'mode':'replace','acknowledge_media_rights':'true'}
            result=client.post('/api/deck/import-bundle',params=params,content=sample_zip(),headers={'Content-Type':'application/zip'})
            assert result.status_code==200,result.text
            saved=result.json()
            assert saved['imported_count']==6
            assert len(saved['rounds'])==6
            assert all(q['media'].startswith('https://') for q in saved['rounds'][1:])
            assert len(client.get('/api/deck').json()['rounds'])==6
            assert client.post('/api/deck/import-bundle',params=params,content=sample_zip(),headers={'Content-Type':'application/zip'}).status_code==409
            params.update({'revision':saved['revision'],'mode':'append'})
            appended=client.post('/api/deck/import-bundle',params=params,content=sample_zip(),headers={'Content-Type':'application/zip'})
            assert appended.status_code==200,appended.text
            assert len(appended.json()['rounds'])==12


def test_failed_media_does_not_overwrite_deck():
    with tempfile.TemporaryDirectory() as folder:
        store=Store();store.url='';store.path=Path(folder)/'test.sqlite'
        with patch.object(main,'store',store),patch.dict(os.environ,{'BLOB_READ_WRITE_TOKEN':'test-not-real'}), \
             patch.object(main,'collect_assets',side_effect=RuntimeError('publisher offline')):
            client=TestClient(main.app)
            previous=client.get('/api/deck').json()
            with pytest.raises(RuntimeError):
                client.post('/api/deck/import-bundle',params={'revision':previous['revision'],'acknowledge_media_rights':'true'},content=sample_zip(),headers={'Content-Type':'application/zip'})
            assert client.get('/api/deck').json()['revision']==previous['revision']


def test_invalid_bundle_returns_422_without_import():
    with tempfile.TemporaryDirectory() as folder:
        store=Store();store.url='';store.path=Path(folder)/'test.sqlite'
        with patch.object(main,'store',store):
            client=TestClient(main.app);revision=client.get('/api/deck').json()['revision']
            result=client.post('/api/deck/import-bundle',params={'revision':revision,'acknowledge_media_rights':'true'},content=b'bad zip',headers={'Content-Type':'application/zip'})
            assert result.status_code==422
            assert client.get('/api/deck').json()['revision']==revision


def test_can_import_embedded_media_without_remote_download():
    photo=tiny_jpeg()
    question={'title':'Example', 'kind':'image','answer':'HUMAN','media':'assets/photo.jpg','context':'Real image?'}
    manifest={'format':'icebreaker-deck-bundle','version':1,'media':{'assets/photo.jpg':{}}}
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('manifest.json',json.dumps(manifest))
        z.writestr('questions.json',json.dumps({'schema_version':1,'rounds':[question]}))
        z.writestr('assets/photo.jpg',photo)
    rounds,media,files=read_bundle(out.getvalue())
    assert len(files['assets/photo.jpg'])>100
    assert len(rounds)==1


def test_jira_overlay_fits_and_keeps_right_side():
    frame=Image.new('RGB',(1000,617),'white')
    from PIL import ImageDraw
    ImageDraw.Draw(frame).rectangle((660,0,999,616),fill='orange')
    out=io.BytesIO();frame.save(out,'PNG')
    jpeg=normalize_image(out.getvalue(),'jira-story-overlay')
    img=Image.open(io.BytesIO(jpeg))
    assert img.size==(1000,617)
    assert img.getpixel((700,100))[0]>200
    assert img.getpixel((30,60)) != (255,255,255)
