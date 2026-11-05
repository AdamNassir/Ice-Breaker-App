"""End-to-end team rankings for a variable-length IceBreaker deck.

Exercises real FastAPI room transitions and scores; all timers use patched wall time
rather than waiting.  Covers the minimum deck, six-question seminar and the
maximum accepted 200-question deck, including ties and restart-safe final state.
"""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
import main
from store import Store


class FinalTeamRankingsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {"DATABASE_URL": "", "VERCEL": "", "PRESENTER_PASSWORD": ""})
        self.env.start()
        store = Store()
        store.path = Path(self.temp.name) / "rankings.sqlite3"
        self.stored = patch.object(main, "store", store)
        self.stored.start()
        self.client = TestClient(main.app)

    def tearDown(self):
        self.client.close()
        self.stored.stop()
        self.env.stop()
        self.temp.cleanup()

    def run_deck(self, size):
        deck = [{"title": f"Question {i+1}", "kind": "text", "body": f"Content {i+1}",
                 "answer": "AI" if i % 2 == 0 else "HUMAN"} for i in range(size)]
        created = self.client.post("/api/rooms", json={"title": "Ranking test", "seconds": 5, "deck": deck})
        self.assertEqual(created.status_code, 200, created.text)
        code = created.json()["code"]
        base = f"/api/rooms/{code}"
        host = {"Authorization": "Bearer " + created.json()["token"]}
        players = []
        for name in ("Alpha captain", "Beta captain", "Gamma captain", "Delta captain"):
            joined = self.client.post(base + "/join", json={"nickname": name})
            self.assertEqual(joined.status_code, 200, joined.text)
            players.append({"Authorization": "Bearer " + joined.json()["token"]})
        team_ids = []
        for name, player in zip(("Alpha", "Beta", "Gamma", "Delta"), players):
            made = self.client.post(base + "/teams", json={"name": name}, headers=player)
            self.assertEqual(made.status_code, 200, made.text)
            team_ids.append(made.json()["me"]["team_id"])
        def state(headers=host):
            got = self.client.get(base + "/state", headers=headers)
            self.assertEqual(got.status_code, 200, got.text)
            return got.json()
        def control(action):
            last = state()
            result = self.client.post(base + "/control", headers=host,
                                      json={"action": action, "revision": last["revision"]})
            self.assertEqual(result.status_code, 200, result.text)
            return result.json()
        running = control("start")
        self.assertEqual(running["phase"], "live")
        self.assertEqual(running["round_count"], size)
        self.assertEqual(running["ranking_type"], "teams")
        for i, question in enumerate(deck):
            self.assertEqual(running["round_index"], i)
            self.assertEqual(running["round_number"], i + 1)
            self.assertEqual(running["completed_rounds"], i)
            self.assertEqual(running["phase"], "live")
            answer = question["answer"]
            wrong = "HUMAN" if answer == "AI" else "AI"
            # Alpha always correct; Beta on even-indexed rounds; Gamma and
            # Delta always wrong. Both ties and gaps appear in the ranking.
            votes = (answer, answer if i % 2 == 0 else wrong, wrong, wrong)
            for player, choice in zip(players, votes):
                vote = self.client.post(base + "/vote", headers=player,
                                        json={"answer": choice, "round_index": i})
                self.assertEqual(vote.status_code, 200, vote.text)
            expiry = running["deadline"]
            with patch.object(main.time, "time", return_value=expiry + 1):
                pooling = state()
                self.assertEqual(pooling["phase"], "pooling")
                self.assertEqual(pooling["completed_rounds"], i)
            with patch.object(main.time, "time", return_value=expiry + main.POOL_SECONDS + 2):
                revealed = state()
                self.assertEqual(revealed["phase"], "revealed")
                self.assertEqual(revealed["completed_rounds"], i + 1)
                self.assertEqual(revealed["ranking_type"], "teams")
                again = state()
                self.assertEqual(again["revision"], revealed["revision"])
                self.assertEqual(again["leaderboard"], revealed["leaderboard"])
            if i < size - 1:
                running = control("next")
                self.assertEqual(running["phase"], "live")
            else:
                # Last answer is revealed until the presenter explicitly shows
                # the final results; pressing the button works regardless of N.
                final = control("next")
        self.assertEqual(final["phase"], "finished")
        self.assertIsNone(final["deadline"])
        self.assertEqual(final["round_count"], size)
        self.assertEqual(final["round_number"], size)
        self.assertEqual(final["completed_rounds"], size)
        self.assertIsNone(final["question"])
        self.assertIsNone(final["reveal"])
        self.assertEqual(final["ranking_type"], "teams")
        self.assertEqual([t["nickname"] for t in final["leaderboard"]], ["Alpha", "Beta", "Delta", "Gamma"])
        self.assertEqual([t["rank"] for t in final["leaderboard"]], [1, 2 if size > 1 else 1, 3 if size > 1 else 3, 3])
        self.assertEqual(final["leaderboard"][0]["correct"], size)
        self.assertEqual(final["leaderboard"][1]["correct"], (size + 1) // 2)
        self.assertEqual(final["leaderboard"][2]["correct"], 0)
        expected_alpha = sum(main.BASE_POINTS + min(i * main.STREAK_STEP, main.MAX_STREAK_BONUS)
                             for i in range(size))
        self.assertEqual(final["leaderboard"][0]["score"], expected_alpha)
        self.assertEqual(final["leaderboard"][1]["score"], ((size + 1) // 2) * main.BASE_POINTS)
        for player, tid in zip(players, team_ids):
            snapshot = state(player)
            team = next(t for t in final["leaderboard"] if t["id"] == tid)
            self.assertEqual(snapshot["phase"], "finished")
            self.assertEqual(snapshot["leaderboard"], final["leaderboard"])
            self.assertEqual(snapshot["me"]["rank"], team["rank"])
            self.assertEqual(snapshot["me"]["score"], team["score"])
            self.assertEqual(len(snapshot["me"]["history"]), size)
        # The result survives subsequent polls and cannot score again.
        again = state()
        self.assertEqual(again["leaderboard"], final["leaderboard"])
        self.assertEqual(again["revision"], final["revision"])
        declined = self.client.post(base + "/control", headers=host,
                                    json={"action": "next", "revision": final["revision"]})
        self.assertEqual(declined.status_code, 409)
        self.assertEqual(state()["leaderboard"], final["leaderboard"])

    def test_one_question(self):
        self.run_deck(1)

    def test_two_questions(self):
        self.run_deck(2)

    def test_six_questions(self):
        self.run_deck(6)

    def test_seventeen_questions(self):
        self.run_deck(17)

    def test_maximum_two_hundred_questions(self):
        self.run_deck(200)

    def test_empty_deck_and_over_limit_rejected(self):
        self.assertEqual(self.client.post('/api/rooms', json={'deck': []}).status_code, 503)
        item = {"title": "test", "kind": "text", "body": "content", "answer": "AI"}
        self.assertIn(self.client.post('/api/rooms', json={'deck': [item] * 201}).status_code, (422, 503))


if __name__ == '__main__':
    unittest.main()
