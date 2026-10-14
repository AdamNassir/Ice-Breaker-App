# Completed update — team composition after QR/pseudonym entry

## Resulting behavior

- The supplied Ice_Breaker_Game_App_draft.zip is the sole baseline. After scanning its room QR and choosing a pseudonym, players see Create a team or Join a team in the phone lobby.
- Creating accepts a visible group name up to 40 characters, takes the creator name from their authenticated pseudonym and includes them as the first member. Joining shows every created team as Group name | Creator name, with the current member pseudonyms underneath.
- The directory updates while people create/join teams. Polling preserves partly typed names, focused join controls and unchanged roster DOMs. A browser refresh restores the selected team from the server. Same group names are allowed, distinguished by creator/member lists.
- A player selects one team once. Duplicate/retried requests do not create extra groups or members. Creation/joining closes atomically with presenter Start; server checks prevent a late request from changing a started game's membership. Only authenticated players in that room can select teams.
- The presenter retains the central QR lobby and sees team/member counts. Teams organize players; voting, scores, streaks and final placements remain individual. The presenter chooses when to start; unassigned/late players retain individual play. A selected team's label appears on the member's phone during questions. The question, reveal and presenter final screens retain their existing layout.
- Teams are stored in the existing room JSON and use the same SQLite/Supabase transaction lock as Start. No new dependency or database migration. Existing rooms without team fields keep their original flow; new rooms enable teams.
- Both deck files, every question/media asset, logos, the local manager and protected watcher/check files are unchanged byte-for-byte.

## Install / redeploy

1. Extract the complete updated ZIP. Keep your own .env, database and installed dependencies from your local setup. The delivery omits local credentials, stored games and node_modules.
2. Deploy the changed server and static files manually, then create a NEW room. No SQL migration or dependency change is needed. Old room snapshots keep their previous join flow.
3. Rehearse with two phones: one creates a group, the other chooses Join a team, recognizes the creator and joins. Verify both member lists before pressing Start.

## Validation

- 50 Python tests and the complete python check_project.py gate pass in the working project and a fresh ZIP extraction.
- Six team API tests cover names, authorization/room isolation, derived creator identity, duplicate names/retries/concurrency, one-team membership, a simultaneous Start/join race, locks after start/reveal/results, refreshed membership, older rooms and unchanged individual scoring.
- A real local FastAPI server plus multiple phone DOMs exercise the QR-prefilled form, choices, directory/member updates, typing/focus preserved through polls, restored membership in a new DOM, safe text rendering, closure at start, team badges and normal voting. Existing API/manager/HTML resource/QR/timer/zoom/identity reveal/Enter/results/confetti/bonus checks pass.
- Source/archive byte comparisons, manifest and CRC checks verify all changed/added paths against the uploaded draft. Both deck files and every media asset match the draft. Runtime dependencies, caches and generated QA files are not delivered.

## Limits

The installed Playwright package has no browser executable here, so native-browser screenshots and physical-phone/projector rehearsal were unavailable. DOM checks cover the shipped HTML/CSS and real local API. Live Supabase/Vercel, capacity and native Windows watcher operation were not tested or deployed.

## Modified files relative to the supplied draft

- `CreationInstructions.md`
- `ReadMe.md`
- `UpdateGuide.md`
- `Verification.md`
- `main.py`
- `static/app.js`
- `static/index.html`
- `static/presenter.html`
- `static/style.css`
- `tests/run_frontend.py`

## Added source files

- `tests/frontend/teams.cjs`
- `tests/test_teams.py`

## Source files removed

None.

## Local runtime files excluded from the delivery

- `.env`
- `game.sqlite3`
- `download` (local artifact)
- `tests/frontend/node_modules/**`

The original uploaded ZIP is not changed on disk. These files are excluded from the clean deliverable; installed test dependencies can be restored with the existing setup instructions.
