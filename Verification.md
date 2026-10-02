# Verification — October 2, 2026

## Passed

- Python 3.12 syntax checks for all Python source files.
- JavaScript syntax check with `node --check static/app.js`.
- Eight API test cases in `tests/test_game.py`, using temporary SQLite databases:
  - Full ten-round playthrough, reveal, manual progression and final results.
  - Correct streak progression and a 1,750-point perfect score.
  - Wrong/missing answers reset streaks.
  - Five concurrent attempts to vote produce exactly one accepted vote.
  - Duplicate, stale-round and late votes are rejected.
  - Stale presenter actions and player attempts to control rounds are rejected.
  - Correct answers, explanations and token hashes stay out of live public state.
  - Pseudonym uniqueness, refresh identity, room expiry and configuration guards.
  - Both HTML pages, styles, JavaScript and all four image URLs are served.
- Live DOM integration against a local FastAPI server using the actual delivered HTML and JavaScript:
  - Presenter form creates a room; player form joins with a pseudonym.
  - Presenter start reveals the first question and activates voting.
  - Correct answers are hidden during the timer; vote buttons lock after acceptance.
  - Two real five-second rounds settle through normal polling.
  - Player score changes from 100 to 225, with streaks 1 and 2.
  - Reveal appears on both views; next round waits for a separate presenter start.
  - No JavaScript runtime errors in this integration run.
- Human sample source retrieval and bundled image decoding checked. Generated image assets were inspected before inclusion; CPython license included.

## Not verified here

- Full rendered visual/browser QA: local Chromium launch failed in this execution environment. DOM integration does not establish pixel-perfect rendering, actual mobile Safari behavior or accessibility compliance. Rehearse on the intended phone and projector browsers.
- Live Supabase connection, custom-role migration and Vercel deployment: no account credentials were supplied. The PostgreSQL path and deployment instructions use current official documentation, but a real cloud smoke test remains required.
- Production concurrency/load: the 200-player cap is a storage/abuse bound, not a tested capacity guarantee.
- Audio playback: supported by the renderer, but no audio round is bundled.

## Before the event

Run the README's cloud setup, confirm `/api/health` reports Supabase PostgreSQL, and play through from the actual presenter laptop and two phones. Verify the shared link is reachable without a Vercel sign-in, images fit the projected screen, refresh restores the player, the timer closes votes and final standings appear. For a larger audience, rehearse with the intended number of devices on the actual network and hosting plan.
