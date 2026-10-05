"""Meaningful game invariants; no waiting for real timers or external accounts."""
import os
import sys
import tempfile
import unittest
import base64
import shutil
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
import main
from store import Store
from question_content import parse_deck, validate_rounds


class GameTests(unittest.TestCase):
    def test_bundled_managed_deck_matches_fallback_and_assets(self):
        root = Path(__file__).resolve().parents[1]
        managed = parse_deck((root / 'questions.json').read_bytes(), root)
        self.assertEqual(managed, validate_rounds(main.ROUNDS, root))
        self.assertEqual(len(managed), 10)
        self.assertEqual(sum(q['answer'] == 'AI' for q in managed), 7)
        self.assertEqual([q['kind'] for q in managed].count('image'), 8)
        self.assertEqual([q['kind'] for q in managed].count('text'), 2)
        self.assertEqual([q['kind'] for q in managed].count('audio'), 0)
        self.assertEqual([q['kind'] for q in managed].count('video'), 0)
        self.assertGreater(len(managed[4]['body'].split()), 70)
        self.assertEqual(managed[2]['answer'], 'AI')
        self.assertEqual(managed[4]['answer'], 'AI')
        self.assertEqual(managed[7]['answer'], 'AI')
        self.assertEqual(managed[4]['reveal_sources'], [])
        self.assertTrue(all(q['title'] and q['context'] for q in managed))
        self.assertIn('manager’s reply', managed[8]['context'])
        self.assertEqual(managed[1]['media'], '/static/images/sample24.jpg')
        self.assertEqual(managed[6]['media'], '/static/images/sample25.png')
        self.assertEqual(managed[6]['answer'], 'AI')
        self.assertTrue(all(not q.get('media_url') for q in managed))

    def test_supplied_logos_are_served_on_all_entry_views(self):
        for name in ('logiclever.png', 'totalenergies.png'):
            response = self.client.get('/static/branding/' + name)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.headers['content-type'].startswith('image/png'))
            self.assertTrue(response.content.startswith(b'\x89PNG\r\n\x1a\n'))
            for route in ('/', '/presenter', '/bonus'):
                self.assertIn('/static/branding/' + name, self.client.get(route).text)

    def test_workflow_asset_and_creation_brief_privacy(self):
        self.assertEqual(self.client.get('/static/workflow.js').status_code, 200)
        self.assertIn('/static/workflow.js', self.client.get('/').text)
        self.assertIn('/static/workflow.js', self.client.get('/bonus').text)
        for path in ('/CreationInstructions.md', '/AGENTS.md', '/UpdateGuide.md',
                     '/agent_watch.py', '/agent_config.json', '/AgentSetup.md',
                     '/check_project.py', '/.agent/state.json', '/tests/frontend/game.cjs'):
            self.assertEqual(self.client.get(path).status_code, 404)
        before = self.state(self.p1)
        self.client.get('/static/workflow.js')
        self.assertEqual(self.state(self.p1)['me'], before['me'])

    def test_lobby_withholds_first_question_and_bonus_is_unscored(self):
        before = self.state(self.p1)
        self.assertEqual(before['phase'], 'lobby')
        self.assertIsNone(before['question'])
        response = self.client.get('/bonus')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Was this game made with AI or not ?', response.text)
        self.assertEqual(self.client.get('/static/bonus.js').status_code, 200)
        after = self.state(self.p1)
        self.assertEqual(before['me'], after['me'])
        self.assertEqual(after['phase'], 'lobby')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        # Verify the bundled game independently of any deck the presenter saved.
        shutil.copytree(main.ROOT / 'static', Path(self.temp.name) / 'static')
        self.root_patch = patch.object(main, 'ROOT', Path(self.temp.name))
        self.root_patch.start()
        self.environment = patch.dict(os.environ, {"DATABASE_URL": "", "PRESENTER_PASSWORD": "", "VERCEL": ""})
        self.environment.start()
        main.store = Store()
        main.store.path = Path(self.temp.name) / "test.sqlite3"
        self.client = TestClient(main.app)
        self.room = self.client.post('/api/rooms', json={"seconds": 5}).json()
        self.code = self.room['code']
        self.host = {"Authorization": "Bearer " + self.room['token']}
        self.p1 = self.join('Ada')
        self.p2 = self.join('Linus')

    def tearDown(self):
        self.client.close()
        self.environment.stop()
        self.root_patch.stop()
        self.temp.cleanup()

    def join(self, name):
        data = self.client.post(f'/api/rooms/{self.code}/join', json={"nickname": name}).json()
        return {"Authorization": "Bearer " + data['token']}

    def state(self, headers=None):
        return self.client.get(f'/api/rooms/{self.code}/state', headers=headers or self.host).json()

    def control(self, action):
        return self.client.post(f'/api/rooms/{self.code}/control', headers=self.host,
                                json={"action": action, "revision": self.state()['revision']})

    def expire(self):
        with main.store.room(self.code) as room:
            room['deadline'] = 0

    def vote(self, headers, answer, index=0):
        return self.client.post(f'/api/rooms/{self.code}/vote', headers=headers,
                                json={"answer": answer, "round_index": index})

    def test_complete_game_streak_scores_and_results(self):
        self.assertEqual(self.control('start').status_code, 200)
        for index, question in enumerate(main.ROUNDS):
            self.assertEqual(self.state()['phase'], 'live')
            live = self.state(self.p1)
            self.assertEqual(live['duration'], 5)
            self.assertEqual(live['question'].get('difficulty'), question.get('difficulty'))
            for private_field in ('answer', 'explanation', 'source', 'source_url',
                                  'technical_note', 'discussion', 'technical_source_url',
                                  'image_reveal', 'image_highlight', 'reveal_sources'):
                self.assertNotIn(private_field, live['question'])
            self.assertEqual(self.vote(self.p1, question['answer'], index).status_code, 200)
            wrong = 'HUMAN' if question['answer'] == 'AI' else 'AI'
            self.vote(self.p2, wrong, index)
            # Use mocked time rather than modifying deadline: players joined before it.
            deadline = self.state()['deadline']
            with patch.object(main.time, 'time', return_value=deadline + 1):
                s = self.state(self.p1)
                self.assertEqual(s['phase'], 'revealed')
                self.assertEqual(s['reveal']['answer'], question['answer'])
                self.assertEqual(s['reveal'].get('image_reveal', ''), question.get('image_reveal', ''))
                self.assertEqual(s['reveal'].get('image_highlight'), question.get('image_highlight'))
                self.assertEqual(s['reveal'].get('reveal_sources', []), question.get('reveal_sources', []))
                self.assertEqual(s['reveal'].get('technical_note', ''), question.get('technical_note', ''))
                self.assertEqual(s['reveal'].get('discussion'), question.get('discussion'))
                score = s['me']['score']
                self.assertEqual(self.state(self.p1)['me']['score'], score)
            advanced = self.control('next')
            self.assertEqual(advanced.status_code, 200)
            if index < len(main.ROUNDS) - 1:
                self.assertEqual(advanced.json()['phase'], 'live')
                self.assertEqual(advanced.json()['round_index'], index + 1)
                self.assertEqual(advanced.json()['answered_count'], 0)
                self.assertIsNone(advanced.json()['reveal'])
                self.assertIsNone(self.state(self.p1)['me']['vote'])
        final = self.state(self.p1)
        self.assertEqual(final['phase'], 'finished')
        self.assertEqual(final['me']['score'], 1750)
        self.assertEqual(final['me']['streak'], 10)
        self.assertEqual(final['me']['correct'], 10)
        self.assertEqual(final['leaderboard'][1]['score'], 0)
        self.assertEqual(self.control('start').status_code, 409)

    def test_presenter_ten_second_timer_wins_every_round_and_closes_at_deadline(self):
        room = self.client.post('/api/rooms', json={"seconds": 10}).json()
        code = room['code']
        host = {"Authorization": "Bearer " + room['token']}
        player = self.client.post(f'/api/rooms/{code}/join', json={"nickname": "Timer tester"}).json()
        headers = {"Authorization": "Bearer " + player['token']}
        origin = main.time.time()
        with main.store.room(code) as saved:
            for index, question in enumerate(saved['rounds']):
                question['seconds'] = 25 if index % 2 else 120
        for index in range(10):
            start = origin + index * 100
            with patch.object(main.time, 'time', return_value=start):
                state = self.client.get(f'/api/rooms/{code}/state', headers=host).json()
                response = self.client.post(f'/api/rooms/{code}/control', headers=host,
                                            json={"action": "start" if index == 0 else "next", "revision": state['revision']})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()['phase'], 'live')
                self.assertEqual(response.json()['round_index'], index)
                self.assertIsNone(response.json()['reveal'])
                self.assertEqual(response.json()['duration'], 10)
                self.assertEqual(response.json()['deadline'], start + 10)
            with patch.object(main.time, 'time', return_value=start + 9.99):
                self.assertEqual(self.client.get(f'/api/rooms/{code}/state', headers=headers).json()['phase'], 'live')
            with patch.object(main.time, 'time', return_value=start + 10):
                late = self.client.post(f'/api/rooms/{code}/vote', headers=headers,
                                       json={"answer": "AI", "round_index": index})
                self.assertEqual(late.status_code, 409)
                state = self.client.get(f'/api/rooms/{code}/state', headers=host).json()
                self.assertEqual(state['phase'], 'revealed')
            with patch.object(main.time, 'time', return_value=start + 50):
                paused = self.client.get(f'/api/rooms/{code}/state', headers=host).json()
                self.assertEqual(paused['phase'], 'revealed')
                self.assertEqual(paused['round_index'], index)
        with patch.object(main.time, 'time', return_value=start + 50):
            final = self.client.post(f'/api/rooms/{code}/control', headers=host,
                                    json={"action": "next", "revision": paused['revision']})
            self.assertEqual(final.status_code, 200)
            self.assertEqual(final.json()['phase'], 'finished')

    def test_answer_secrecy_auth_and_player_control(self):
        self.control('start')
        s = self.state(self.p1)
        self.assertIsNone(s['reveal'])
        self.assertNotIn('answer', s['question'])
        self.assertNotIn('explanation', s['question'])
        self.assertNotIn('token', str(s))
        response = self.client.get(f'/api/rooms/{self.code}/state')
        self.assertEqual(response.status_code, 401)
        response = self.client.post(f'/api/rooms/{self.code}/control', headers=self.p1,
                                   json={"action": "next", "revision": s['revision']})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.vote(self.host, 'AI').status_code, 403)
        self.assertEqual(self.client.get('/Content.py').status_code, 404)

    def test_duplicate_late_stale_votes_and_controls(self):
        self.control('start')
        revision = self.state()['revision']
        self.assertEqual(self.vote(self.p1, 'AI').status_code, 200)
        self.assertEqual(self.vote(self.p1, 'HUMAN').status_code, 409)
        self.assertEqual(self.state(self.p1)['me']['vote'], 'AI')
        self.assertIsNone(self.state(self.p2)['me']['vote'])
        deadline = self.state()['deadline']
        with patch.object(main.time, 'time', return_value=deadline + 1):
            self.assertEqual(self.vote(self.p2, 'AI').status_code, 409)
            self.assertEqual(self.state()['phase'], 'revealed')
        self.control('next')
        stale = self.client.post(f'/api/rooms/{self.code}/control', headers=self.host,
                                json={"action":"next", "revision":revision})
        self.assertEqual(stale.status_code, 409)
        self.assertEqual(self.control('start').status_code, 409)
        self.assertEqual(self.state()['phase'], 'live')
        self.assertEqual(self.vote(self.p2, 'HUMAN', 0).status_code, 409)

    def test_concurrent_next_starts_exactly_one_round(self):
        self.control('start')
        self.expire()
        revealed = self.state()
        self.assertEqual(revealed['phase'], 'revealed')
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(lambda _: self.client.post(
                f'/api/rooms/{self.code}/control', headers=self.host,
                json={"action": "next", "revision": revealed['revision']}).status_code, range(5)))
        self.assertEqual(results.count(200), 1)
        self.assertEqual(results.count(409), 4)
        live = self.state()
        self.assertEqual(live['phase'], 'live')
        self.assertEqual(live['round_index'], 1)
        self.assertEqual(live['revision'], revealed['revision'] + 1)
        self.assertEqual(live['duration'], 5)

    def test_concurrent_duplicate_vote_is_atomic(self):
        self.control('start')
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(lambda _: self.vote(self.p1, 'AI').status_code, range(5)))
        self.assertEqual(results.count(200), 1)
        self.assertEqual(results.count(409), 4)
        self.assertEqual(self.state()['answered_count'], 1)

    def test_wrong_and_missing_answers_break_streak(self):
        self.control('start')
        for index in range(3):
            if index < 2:
                answer = main.ROUNDS[index]['answer'] if index == 0 else ('AI' if main.ROUNDS[index]['answer']=='HUMAN' else 'HUMAN')
                self.vote(self.p1, answer, index)
            deadline = self.state()['deadline']
            with patch.object(main.time, 'time', return_value=deadline+1):
                self.state()
            self.control('next')
        p = self.state(self.p1)['me']
        self.assertEqual(p['score'], 100)
        self.assertEqual(p['streak'], 0)
        self.assertEqual(len(p['history']), 3)

    def test_unique_nicknames_expiry_and_refresh(self):
        duplicate = self.client.post(f'/api/rooms/{self.code}/join', json={"nickname":" ada "})
        self.assertEqual(duplicate.status_code, 409)
        before = self.state(self.p1)['me']['id']
        self.assertEqual(self.state(self.p1)['me']['id'], before)
        with main.store.room(self.code) as room:
            room['expires_at'] = 0
        self.assertEqual(self.client.get(f'/api/rooms/{self.code}/state', headers=self.p1).status_code, 410)

    def test_production_configuration_and_password(self):
        with patch.dict(os.environ, {"VERCEL":"1"}):
            self.assertEqual(self.client.post('/api/rooms', json={}).status_code, 503)
        with patch.dict(os.environ, {"PRESENTER_PASSWORD":"correct password"}):
            self.assertEqual(self.client.post('/api/rooms', json={}).status_code, 403)
            self.assertEqual(self.client.post('/api/rooms', json={"password":"correct password"}).status_code, 200)
        with patch.dict(os.environ, {"VERCEL":"1"}):
            self.assertEqual(self.client.get('/api/health').status_code, 503)

    def test_media_and_pages_exist(self):
        for url in ['/', '/presenter', '/static/style.css', '/static/imagestyle.css', '/static/app.js', '/static/media.js', '/static/imagezoom.js']:
            self.assertEqual(self.client.get(url).status_code, 200)
        for question in main.ROUNDS:
            if question.get('media'):
                self.assertEqual(self.client.get(question['media']).status_code, 200)

    def test_room_qr_access_and_svg(self):
        url = f'/api/rooms/{self.code}/qr'
        self.assertEqual(self.client.get(url).status_code, 401)
        self.assertEqual(self.client.get(url, headers=self.p1).status_code, 403)
        response = self.client.get(url, headers=self.host)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['cache-control'], 'no-store')
        result = response.json()
        self.assertEqual(result['join_url'], self.room['join_url'])
        matrix = result['qr_matrix']
        self.assertTrue(21 <= len(matrix) <= 185)
        self.assertTrue(all(len(row) == len(matrix) for row in matrix))
        self.assertTrue(all(type(cell) is bool for row in matrix for cell in row))
        # Four quiet-zone modules on every edge are necessary for phone scanning.
        self.assertTrue(all(not cell for row in matrix[:4] + matrix[-4:] for cell in row))
        self.assertTrue(all(not cell for row in matrix for cell in row[:4] + row[-4:]))
        self.assertTrue(any(cell for row in matrix for cell in row))
        self.assertTrue(result['qr_data_uri'].startswith('data:image/svg+xml;base64,'))
        svg = base64.b64decode(result['qr_data_uri'].split(',', 1)[1])
        document = ET.fromstring(svg)
        self.assertTrue(document.tag.endswith('svg'))
        self.assertTrue(document.findall('{http://www.w3.org/2000/svg}path'))
        self.assertNotIn(self.room['token'], svg.decode())
        self.assertNotIn('Bearer', svg.decode())
        self.assertEqual(self.client.get(url, headers=self.host).json(), result)

    def test_room_qr_public_url_and_older_rooms(self):
        with patch.dict(os.environ, {"PUBLIC_BASE_URL":"https://icebreaker.example.test"}):
            room = self.client.post('/api/rooms', json={}).json()
            headers = {"Authorization":"Bearer " + room['token']}
            result = self.client.get(f"/api/rooms/{room['code']}/qr", headers=headers).json()
            self.assertEqual(result['join_url'], f"https://icebreaker.example.test/?room={room['code']}")
            with main.store.room(room['code']) as saved:
                del saved['join_url']
            fallback = self.client.get(f"/api/rooms/{room['code']}/qr", headers=headers).json()
            self.assertEqual(fallback['join_url'], result['join_url'])


if __name__ == '__main__':
    unittest.main()
