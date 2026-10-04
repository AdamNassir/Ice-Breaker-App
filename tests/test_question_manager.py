"""Local editing, persistence, upload and game integration regressions."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
import main
import question_manager
from question_content import DeckError, load_rounds
from store import Store


class ManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "static/images").mkdir(parents=True)
        (self.root / "static/audio").mkdir(parents=True)
        self.env = patch.dict(os.environ, {"DATABASE_URL": "", "PRESENTER_PASSWORD": "", "VERCEL": ""})
        self.env.start()
        self.starter = {"title": "Starter", "kind": "text", "body": "Original text.", "answer": "HUMAN"}
        self.client = TestClient(question_manager.create_manager(self.root, [self.starter]), base_url="http://127.0.0.1:8765")
        self.deck = self.client.get('/api/deck').json()
        self.headers = {"X-Manager-Token": self.deck['manager_token'], "Origin": "http://127.0.0.1:8765"}

    def tearDown(self):
        self.client.close()
        self.env.stop()
        self.temp.cleanup()

    def save(self, rounds, revision=None, headers=None):
        return self.client.put('/api/deck', json={"revision": revision or self.deck['revision'], "rounds": rounds}, headers=headers or self.headers)

    def upload(self, content=b'example bytes', kind='image', extension='.png'):
        return self.client.post(f'/api/media?kind={kind}&extension={extension}', content=content, headers=self.headers)

    def test_save_unicode_exact_code_backup_and_revision_conflict(self):
        body = 'def example():\n    return "Café \\ quoted"\n# Never executed as Python.'
        q = {"title": "Code", "kind": "code", "body": body, "answer": "AI", "seconds": 45}
        response = self.save([q])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(load_rounds(self.root)[0]['body'], body)
        backup = next((self.root / '.question-manager-backups').glob('*.json'))
        self.assertEqual(json.loads(backup.read_text())['rounds'][0]['title'], 'Starter')
        self.assertEqual(self.save([self.starter]).status_code, 409)
        self.assertEqual(load_rounds(self.root)[0]['title'], 'Code')
        self.assertNotEqual(response.json()['revision'], self.deck['revision'])
        self.assertFalse(list(self.root.glob('.questions-*.tmp')))

    def test_local_token_origin_host_and_vercel_guards(self):
        payload = {"revision": self.deck['revision'], "rounds": [self.starter]}
        self.assertEqual(self.client.put('/api/deck', json=payload).status_code, 403)
        self.assertEqual(self.client.put('/api/deck', json=payload, headers={"X-Manager-Token":"wrong"}).status_code, 403)
        self.assertEqual(self.client.put('/api/deck', json=payload, headers={**self.headers,"Origin":"https://outside.example"}).status_code, 403)
        self.assertEqual(self.client.get('/api/deck', headers={"Host":"outside.example"}).status_code, 400)
        with patch.dict(os.environ, {"VERCEL":"1"}):
            self.assertEqual(self.client.get('/api/deck').status_code, 403)
        self.assertFalse((self.root / 'questions.json').exists())

    def test_invalid_empty_missing_media_and_traversal_do_not_write(self):
        bad = [[], [{**self.starter,'title':' '}], [{**self.starter,'answer':'MIXED'}],
               [{**self.starter,'seconds':4}], [{**self.starter,'seconds':5.5}],
               [{**self.starter,'source_url':'javascript:alert(1)'}],
               [{'title':'Image','kind':'image','answer':'HUMAN','media':'/static/images/../audio/x.png'}],
               [{'title':'Image','kind':'image','answer':'HUMAN','media':'/static/images/missing.png'}]]
        for rows in bad:
            with self.subTest(rows=rows):
                self.assertEqual(self.save(rows).status_code, 400)
        self.assertFalse((self.root / 'questions.json').exists())
        self.assertFalse((self.root / '.question-manager-backups').exists())

    def test_upload_paths_bytes_listing_and_no_filename_label(self):
        png = b'\x89PNG\r\n\x1a\nexact bytes are preserved'
        image = self.upload(png).json()['media']
        audio_bytes = b'RIFF\x00\x00\x00\x00WAVEtest'
        audio = self.upload(audio_bytes, 'audio', '.wav').json()['media']
        self.assertRegex(image, r'^/static/images/sample_[a-f0-9]{24}\.png$')
        self.assertEqual((self.root / image.lstrip('/')).read_bytes(), png)
        self.assertEqual((self.root / audio.lstrip('/')).read_bytes(), audio_bytes)
        listing = self.client.get('/api/media').json()
        self.assertEqual(listing['image'][0]['path'], image)
        self.assertEqual(listing['audio'][0]['path'], audio)
        self.assertEqual(self.client.get(image).content, png)
        rows = [{'title':'Picture','kind':'image','answer':'HUMAN','media':image},
                {'title':'Voice','kind':'audio','answer':'AI','media':audio,'body':'Listen.'}]
        self.assertEqual(self.save(rows).status_code, 200)
        self.assertEqual(len(load_rounds(self.root)), 2)
        self.assertEqual(self.upload(extension='.html').status_code, 400)
        self.assertEqual(self.upload(b'').status_code, 400)

    def test_upload_size_rejection_removes_incomplete_file(self):
        with patch.object(question_manager, 'MAX_UPLOAD_BYTES', 4):
            self.assertEqual(self.upload(b'12345').status_code, 413)
            def chunks():
                yield b'123'
                yield b'456'
            response = self.client.post('/api/media?kind=image&extension=.png', content=chunks(), headers=self.headers)
            self.assertEqual(response.status_code, 413)
        self.assertFalse(list((self.root / 'static/images').iterdir()))

    def test_video_upload_save_and_game_round(self):
        content = b'\x00\x00\x00\x18ftypmp42video fixture'
        video = self.upload(content, 'video', '.MP4').json()['media']
        self.assertRegex(video, r'^/static/videos/sample_[a-f0-9]{24}\.mp4$')
        self.assertEqual((self.root / video.lstrip('/')).read_bytes(), content)
        self.assertEqual(self.client.get('/api/media').json()['video'][0]['path'], video)
        self.assertEqual(self.client.get(video).content, content)
        question = {'title':'Video clip', 'kind':'video', 'answer':'AI', 'media':video,
                    'body':'Watch the movement.', 'alt':'A short workshop clip.'}
        self.assertEqual(self.save([question]).status_code, 200)
        self.assertEqual(load_rounds(self.root)[0]['kind'], 'video')
        store = Store()
        store.path = self.root / 'video-game.sqlite3'
        with patch.object(main, 'ROOT', self.root), patch.object(main, 'store', store):
            with TestClient(main.app) as game:
                room = game.post('/api/rooms', json={}).json()
                game.post(f"/api/rooms/{room['code']}/join", json={'nickname':'Video viewer'})
                state = game.post(f"/api/rooms/{room['code']}/control", headers={'Authorization':'Bearer '+room['token']},
                                  json={'action':'start', 'revision':0})
                self.assertEqual(state.status_code, 200)
                public = state.json()['question']
                self.assertEqual(public['kind'], 'video')
                self.assertEqual(public['media'], video)
                self.assertEqual(public['body'], question['body'])
                self.assertNotIn('answer', public)
        self.assertEqual(self.upload(content, 'video', '.exe').status_code, 400)
        self.assertEqual(self.upload(content, 'unknown', '.mp4').status_code, 400)
        current = self.client.get('/api/deck').json()['revision']
        self.assertEqual(self.save([{**question, 'media':'/static/audio/a.mp4'}], current).status_code, 400)
        self.assertEqual(self.save([{**question, 'media':'/static/videos/../images/a.mp4'}], current).status_code, 400)

    def test_repair_malformed_json_preserves_original_backup(self):
        original = b'{broken external edit'
        (self.root / 'questions.json').write_bytes(original)
        data = self.client.get('/api/deck').json()
        self.assertTrue(data['warning'])
        self.assertEqual(data['rounds'], [])
        self.assertEqual(self.save([self.starter], data['revision']).status_code, 200)
        backups = list((self.root / '.question-manager-backups').glob('*.json'))
        self.assertEqual(backups[0].read_bytes(), original)
        self.assertEqual(load_rounds(self.root)[0]['title'], 'Starter')

    def test_missing_media_can_be_repaired_in_starter_and_saved_deck(self):
        image = {'title':'Missing image', 'kind':'image', 'answer':'HUMAN',
                 'media':'/static/images/missing.png'}
        with TestClient(question_manager.create_manager(self.root, [self.starter, image]),
                        base_url='http://127.0.0.1:8765') as client:
            response = client.get('/api/deck')
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(len(data['rounds']), 2)
            self.assertIn('Question 2', data['warning'])
            self.assertIn(image['media'], data['warning'])
            self.assertEqual(client.get('/api/starter').status_code, 200)
            headers = {'X-Manager-Token':data['manager_token']}
            payload = {'revision':data['revision'], 'rounds':data['rounds']}
            self.assertEqual(client.put('/api/deck', json=payload, headers=headers).status_code, 400)
            uploaded = client.post('/api/media?kind=image&extension=.png', content=b'image bytes', headers=headers).json()['media']
            payload['rounds'][1]['media'] = uploaded
            self.assertEqual(client.put('/api/deck', json=payload, headers=headers).status_code, 200)
            (self.root / uploaded.lstrip('/')).unlink()
            repaired = client.get('/api/deck').json()
            self.assertEqual(len(repaired['rounds']), 2)
            self.assertIn(uploaded, repaired['warning'])
            with self.assertRaises(DeckError):
                load_rounds(self.root)
            self.assertEqual(client.put('/api/deck', json={'revision':repaired['revision'], 'rounds':[self.starter]}, headers=headers).status_code, 200)
            self.assertEqual(load_rounds(self.root)[0]['title'], 'Starter')

    def test_new_room_reads_saved_deck_existing_room_keeps_snapshot(self):
        game_store = Store()
        game_store.path = self.root / 'game.sqlite3'
        with patch.object(main, 'ROOT', self.root), patch.object(main, 'ROUNDS', [self.starter]), patch.object(main, 'store', game_store):
            with TestClient(main.app) as game:
                old = game.post('/api/rooms', json={}).json()
                custom = {"title":"New question","kind":"commit","body":"fix: keep this exact text","answer":"AI"}
                self.assertEqual(self.save([custom]).status_code, 200)
                new = game.post('/api/rooms', json={}).json()
                with game_store.room(old['code']) as room:
                    self.assertEqual(room['rounds'][0]['title'], 'Starter')
                with game_store.room(new['code']) as room:
                    self.assertEqual(room['rounds'][0]['title'], 'New question')
                    self.assertEqual(room['rounds'][0]['answer'], 'AI')
                for path in ['/questions.json','/question_manager.py','/manager-assets/app.js','/api/deck']:
                    self.assertEqual(game.get(path).status_code, 404)
                (self.root / 'questions.json').write_text('broken')
                self.assertEqual(game.post('/api/rooms', json={}).status_code, 503)

    def test_manager_assets_and_deck_format(self):
        for path in ['/','/manager-assets/app.js','/manager-assets/style.css']:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['cache-control'], 'no-store')
        (self.root / 'questions.json').write_text(json.dumps({'schema_version':999,'rounds':[self.starter]}))
        with self.assertRaises(DeckError):
            load_rounds(self.root)

    def test_room_creation_reports_deck_source_and_missing_file(self):
        image = {'title':'Picture', 'kind':'image', 'answer':'HUMAN',
                 'media':'/static/images/missing.png'}
        with patch.object(main, 'ROOT', self.root), patch.object(main, 'ROUNDS', [image]):
            with TestClient(main.app) as game:
                fallback = game.post('/api/rooms', json={})
                self.assertEqual(fallback.status_code, 503)
                self.assertIn('Content.py starter deck; questions.json is absent', fallback.json()['detail'])
                self.assertIn('Question 1', fallback.json()['detail'])
                self.assertIn(image['media'], fallback.json()['detail'])
                (self.root / 'questions.json').write_text(json.dumps({'schema_version':1,'rounds':[image]}))
                saved = game.post('/api/rooms', json={})
                self.assertIn('Question deck cannot load (questions.json)', saved.json()['detail'])
                self.assertIn(image['media'], saved.json()['detail'])
                (self.root / 'questions.json').write_text('broken json')
                malformed = game.post('/api/rooms', json={})
                self.assertIn('not valid UTF-8 JSON', malformed.json()['detail'])

    def test_online_audio_video_clips_and_invalid_links(self):
        video = {'title':'Robot clip', 'kind':'video', 'answer':'HUMAN',
                 'media_url':'https://www.youtube.com/watch?v=fn3KWM1kuAw', 'media_start':4,'media_end':18}
        audio = {'title':'Voice clip', 'kind':'audio', 'answer':'AI',
                 'media_url':'https://media.example.test/voice.wav', 'media_start':0,'media_end':7}
        saved = self.save([video,audio])
        self.assertEqual(saved.status_code,200)
        self.assertEqual(load_rounds(self.root)[0]['media_url'],video['media_url'])
        current = saved.json()['revision']
        bad = [{**video,'media_url':'javascript:alert(1)'},
               {**video,'media_url':'https://youtube.com.evil.test/watch?v=fn3KWM1kuAw'},
               {**video,'media_url':'https://www.youtube.com/watch?v=invalid'},
               {**video,'media_url':'https://user:password@example.test/a.mp4'},
               {**video,'media':'/static/videos/missing.mp4'},
               {**video,'media_end':3}, {**video,'media_start':1.5},
               {**audio,'media_url':'https://example.test/page'},
               {**audio,'kind':'image'}]
        for question in bad:
            with self.subTest(question=question):self.assertEqual(self.save([question],current).status_code,400)
        game_store=Store();game_store.path=self.root/'links.sqlite3'
        with patch.object(main,'ROOT',self.root),patch.object(main,'store',game_store):
            with TestClient(main.app) as game:
                room=game.post('/api/rooms',json={}).json()
                game.post(f"/api/rooms/{room['code']}/join",json={'nickname':'Viewer'})
                state=game.post(f"/api/rooms/{room['code']}/control",headers={'Authorization':'Bearer '+room['token']},json={'action':'start','revision':0}).json()
                self.assertEqual(state['question']['media_url'],video['media_url'])
                self.assertEqual(state['question']['media_start'],4)
                self.assertEqual(state['question']['media_end'],18)
                self.assertNotIn('answer',state['question'])


if __name__ == '__main__':
    unittest.main()
