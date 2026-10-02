"""Meaningful game invariants; no waiting for real timers or external accounts."""
import os
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
import main
from store import Store


class GameTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
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
        for index, question in enumerate(main.ROUNDS):
            self.assertEqual(self.control('start').status_code, 200)
            self.assertEqual(self.vote(self.p1, question['answer'], index).status_code, 200)
            wrong = 'HUMAN' if question['answer'] == 'AI' else 'AI'
            self.vote(self.p2, wrong, index)
            # Use mocked time rather than modifying deadline: players joined before it.
            deadline = self.state()['deadline']
            with patch.object(main.time, 'time', return_value=deadline + 1):
                s = self.state(self.p1)
                self.assertEqual(s['phase'], 'revealed')
                self.assertEqual(s['reveal']['answer'], question['answer'])
                score = s['me']['score']
                self.assertEqual(self.state(self.p1)['me']['score'], score)
            self.assertEqual(self.control('next').status_code, 200)
        final = self.state(self.p1)
        self.assertEqual(final['phase'], 'finished')
        self.assertEqual(final['me']['score'], 1750)
        self.assertEqual(final['me']['streak'], 10)
        self.assertEqual(final['me']['correct'], 10)
        self.assertEqual(final['leaderboard'][1]['score'], 0)
        self.assertEqual(self.control('start').status_code, 409)

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
        self.control('start')
        self.assertEqual(self.vote(self.p2, 'HUMAN', 0).status_code, 409)

    def test_concurrent_duplicate_vote_is_atomic(self):
        self.control('start')
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(lambda _: self.vote(self.p1, 'AI').status_code, range(5)))
        self.assertEqual(results.count(200), 1)
        self.assertEqual(results.count(409), 4)
        self.assertEqual(self.state()['answered_count'], 1)

    def test_wrong_and_missing_answers_break_streak(self):
        for index in range(3):
            self.control('start')
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
        for url in ['/', '/presenter', '/static/style.css', '/static/imagestyle.css', '/static/app.js']:
            self.assertEqual(self.client.get(url).status_code, 200)
        for question in main.ROUNDS:
            if question.get('media'):
                self.assertEqual(self.client.get(question['media']).status_code, 200)


if __name__ == '__main__':
    unittest.main()
