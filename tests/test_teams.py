"""Team composition: room authorization, atomic membership and lobby-only writes."""
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
import main
from store import Store


class TeamTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {'DATABASE_URL': '', 'VERCEL': '', 'PRESENTER_PASSWORD': ''})
        self.env.start()
        storage = Store()
        storage.path = Path(self.temp.name) / 'teams.sqlite3'
        self.storage = patch.object(main, 'store', storage)
        self.storage.start()
        self.client = TestClient(main.app)
        self.room = self.client.post('/api/rooms', json={'seconds': 10}).json()
        self.base = '/api/rooms/' + self.room['code']
        self.host = {'Authorization': 'Bearer ' + self.room['token']}
        self.ada = self.join('Ada')
        self.linus = self.join('Linus')

    def tearDown(self):
        self.client.close()
        self.storage.stop()
        self.env.stop()
        self.temp.cleanup()

    def join(self, nickname):
        result = self.client.post(self.base + '/join', json={'nickname': nickname})
        self.assertEqual(result.status_code, 200)
        return {'Authorization': 'Bearer ' + result.json()['token']}

    def state(self, headers=None):
        return self.client.get(self.base + '/state', headers=headers or self.host).json()

    def create(self, name='Data Club', headers=None):
        return self.client.post(self.base + '/teams', json={'name': name}, headers=headers or self.ada)

    def select(self, tid, headers=None):
        return self.client.post(self.base + '/teams/' + tid + '/join', json={}, headers=headers or self.linus)

    def start(self):
        return self.client.post(self.base + '/control', headers=self.host,
                                json={'action': 'start', 'revision': self.state()['revision']})

    def test_create_join_rosters_and_refresh_use_team_scores(self):
        empty = self.state(self.ada)
        self.assertTrue(empty['teams_enabled'])
        self.assertTrue(empty['teams_open'])
        self.assertEqual(empty['teams'], [])
        self.assertIsNone(empty['me']['team_id'])
        created = self.create('  Les   Décodeurs  ').json()
        tid = created['me']['team_id']
        team = created['teams'][0]
        self.assertEqual(team['name'], 'Les Décodeurs')
        self.assertEqual(team['creator'], {'id': created['me']['id'], 'nickname': 'Ada'})
        self.assertEqual([m['nickname'] for m in team['members']], ['Ada'])
        selected = self.select(tid)
        self.assertEqual(selected.status_code, 200)
        self.assertEqual(selected.json()['me']['team_id'], tid)
        self.assertEqual([m['nickname'] for m in self.state()['teams'][0]['members']], ['Ada', 'Linus'])
        self.assertEqual(self.state(self.linus)['me']['team_id'], tid)
        self.assertEqual(self.state(self.ada)['me']['score'], 0)
        self.assertEqual(self.state(self.linus)['me']['score'], 0)
        public = self.state()
        self.assertNotIn('token', str(public))
        self.assertNotIn('host', public)
        self.assertIsNone(public['question'])
        self.assertEqual(self.start().status_code, 200)
        state = self.state(self.ada)
        self.assertFalse(state['teams_open'])
        self.assertEqual(state['teams'][0]['id'], tid)
        self.assertEqual(self.client.post(self.base + '/vote', headers=self.ada,
                         json={'answer': main.ROUNDS[0]['answer'], 'round_index': 0}).status_code, 200)
        with patch.object(main.time, 'time', return_value=state['deadline'] + 1):
            pooling = self.state(self.ada)
            self.assertEqual(pooling['phase'], 'pooling')
            self.assertIsNone(pooling['reveal'])
            self.assertEqual(pooling['team_results'], {})
            self.assertEqual(pooling['me']['score'], 0)
        with patch.object(main.time, 'time', return_value=state['deadline'] + main.POOL_SECONDS + 2):
            revealed = self.state(self.ada)
            self.assertEqual(revealed['phase'], 'revealed')
            self.assertEqual(revealed['team_results'][tid]['answer'], main.ROUNDS[0]['answer'])
            self.assertEqual(revealed['me']['score'], 100)
            self.assertEqual(self.state(self.linus)['me']['score'], 100)
            self.assertEqual(len(revealed['leaderboard']), 1)
            self.assertEqual(revealed['leaderboard'][0]['nickname'], 'Les Décodeurs')

    def test_team_majority_tie_and_no_vote_pooling(self):
        tid = self.create().json()['me']['team_id']
        self.assertEqual(self.select(tid).status_code, 200)
        third = self.join('Grace')
        self.assertEqual(self.select(tid, third).status_code, 200)
        self.start()
        live = self.state()
        correct = main.ROUNDS[0]['answer']
        wrong = 'HUMAN' if correct == 'AI' else 'AI'
        for headers, answer in ((self.ada, correct), (self.linus, correct), (third, wrong)):
            response = self.client.post(self.base + '/vote', headers=headers,
                json={'answer': answer, 'round_index': 0})
            self.assertEqual(response.status_code, 200)
        with patch.object(main.time, 'time', return_value=live['deadline'] + 1):
            pooled = self.state()
            self.assertEqual(pooled['phase'], 'pooling')
            self.assertNotIn('answer', str(pooled['team_results']))
        with patch.object(main.time, 'time', return_value=live['deadline'] + 5):
            revealed = self.state()
            self.assertEqual(revealed['team_results'][tid]['counts'][correct], 2)
            self.assertEqual(revealed['team_results'][tid]['answer'], correct)
            self.assertEqual(revealed['leaderboard'][0]['score'], 100)
            self.assertEqual(self.state(third)['me']['score'], 100)
        self.client.post(self.base + '/control', headers=self.host,
            json={'action': 'next', 'revision': revealed['revision']})
        live = self.state()
        for headers, answer in ((self.ada, 'AI'), (self.linus, 'HUMAN')):
            self.client.post(self.base + '/vote', headers=headers,
                json={'answer': answer, 'round_index': 1})
        with patch.object(main.time, 'time', return_value=live['deadline'] + 1):
            self.state()
        with patch.object(main.time, 'time', return_value=live['deadline'] + 5):
            tied = self.state()
            self.assertIsNone(tied['team_results'][tid]['answer'])
            self.assertTrue(tied['team_results'][tid]['tie'])
            self.assertEqual(tied['leaderboard'][0]['score'], 100)

    def test_authorization_invalid_names_and_room_isolation(self):
        self.assertEqual(self.client.post(self.base + '/teams', json={'name': 'X'}).status_code, 401)
        self.assertEqual(self.create(headers=self.host).status_code, 403)
        for name in (' ', '\x00', 'x' * 41):
            self.assertIn(self.create(name).status_code, (400, 422))
        self.assertEqual(self.state()['teams'], [])
        other = self.client.post('/api/rooms', json={}).json()
        stranger = self.client.post('/api/rooms/' + other['code'] + '/join', json={'nickname': 'Other'}).json()
        foreign = {'Authorization': 'Bearer ' + stranger['token']}
        self.assertEqual(self.create(headers=foreign).status_code, 401)
        created = self.create().json()
        tid = created['me']['team_id']
        self.assertEqual(self.select(tid, headers=self.host).status_code, 403)
        self.assertEqual(self.select(tid, headers=foreign).status_code, 401)
        self.assertEqual(self.select('missing').status_code, 404)
        self.assertIsNone(self.state(self.linus)['me']['team_id'])
        forged = self.client.post(self.base + '/teams', json={'name': 'Another', 'creator_id': created['me']['id']}, headers=self.linus)
        self.assertEqual(forged.status_code, 200)
        self.assertEqual(forged.json()['teams'][1]['creator']['nickname'], 'Linus')

    def test_identical_names_are_distinguished_by_creator_and_membership_is_single(self):
        a = self.create('The Team').json()
        b = self.create('The Team', self.linus).json()
        self.assertEqual([t['name'] for t in b['teams']], ['The Team', 'The Team'])
        self.assertEqual([t['creator']['nickname'] for t in b['teams']], ['Ada', 'Linus'])
        self.assertNotEqual(a['me']['team_id'], b['me']['team_id'])
        self.assertEqual(self.select(a['me']['team_id']).status_code, 409)
        self.assertEqual(self.create('Different').status_code, 409)
        retry = self.create('The Team').json()
        self.assertEqual(len(retry['teams']), 2)
        self.assertEqual(retry['me']['team_id'], a['me']['team_id'])

    def test_concurrent_creates_and_joins_do_not_duplicate_members(self):
        with ThreadPoolExecutor(max_workers=5) as pool:
            created = list(pool.map(lambda _: self.create().json(), range(5)))
        tid = created[0]['me']['team_id']
        self.assertTrue(all(v['me']['team_id'] == tid for v in created))
        self.assertEqual(len(self.state()['teams']), 1)
        with ThreadPoolExecutor(max_workers=5) as pool:
            joined = list(pool.map(lambda _: self.select(tid).status_code, range(5)))
        self.assertEqual(joined, [200] * 5)
        self.assertEqual(len(self.state()['teams'][0]['members']), 2)

    def test_start_race_and_all_post_start_membership_writes_are_locked(self):
        tid = self.create().json()['me']['team_id']
        with ThreadPoolExecutor(max_workers=2) as pool:
            selecting = pool.submit(self.select, tid)
            starting = pool.submit(self.start)
            joined, started = selecting.result(), starting.result()
        self.assertEqual(started.status_code, 200)
        self.assertIn(joined.status_code, (200, 409))
        before = self.state(self.linus)
        self.assertEqual(before['me']['team_id'] == tid, joined.status_code == 200)
        self.assertEqual(self.select(tid).status_code, 409)
        self.assertEqual(self.create('Late team', self.linus).status_code, 409)
        self.assertEqual(self.state()['teams'], before['teams'])
        deadline = before['deadline']
        with patch.object(main.time, 'time', return_value=deadline + 1):
            self.state()
        self.assertEqual(self.select(tid).status_code, 409)
        with main.store.room(self.room['code']) as state:
            state['phase'] = 'finished'
        self.assertEqual(self.create('After results', self.linus).status_code, 409)

    def test_older_rooms_keep_their_existing_flow(self):
        with main.store.room(self.room['code']) as state:
            state.pop('teams')
        older = self.state(self.ada)
        self.assertFalse(older['teams_enabled'])
        self.assertFalse(older['teams_open'])
        self.assertEqual(older['teams'], [])
        self.assertEqual(self.create().status_code, 409)
        self.assertEqual(self.start().status_code, 200)


if __name__ == '__main__':
    unittest.main()
