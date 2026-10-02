# Verification — October 2, 2026

## Passed

### Local question manager update

- Eighteen Python API test cases pass: ten game cases plus eight editor cases covering JSON saving, exact Unicode/code text, raw media copying, neutral filenames, upload size cleanup, invalid fields/missing files/path traversal, local token/origin/host checks, disabled hosted access, backups, malformed-file repair, stale revision rejection and new-room snapshots.
- Existing game tests use an isolated copy of the starter assets, so a presenter's saved custom deck does not change those tests.
- Live integration against separate manager/game servers in an isolated project copy, using the real manager HTML/JavaScript in JSDOM: add text/code/commit questions, import UTF-8 text, upload actual JPEG and WAV bytes, inspect preview elements, reorder/duplicate/delete, recover from a validation error, save/reopen the deck, reject an overwrite from a stale second tab, then create/start a game room from the saved questions. Uploaded files are also served by the game. No JavaScript runtime errors.
- Public game routes do not expose `/api/deck`, `questions.json`, manager assets or the manager Python file. The local editor has a separate entrypoint; save/load needs no Supabase connection or additional dependency.
- Saving a managed JSON deck affects newly created rooms without restarting the local game; existing rooms keep their original questions. The bundled Content.py remains the fallback when JSON is absent.
- Python compilation and JavaScript syntax checks completed for the new modules/assets.


### Technical-deck update

- Ten rounds, five AI/five human originals, nondecreasing levels 1–5, per-round timers 30–60 seconds; 445 seconds total voting time.
- Exact code selection checks against retrieved tagged CPython 3.5.0, Go 1.9 and Redis 3.2.13 source files; the cancellation commit excerpt also matches its retrieved original message after documented omissions. Release/source records and licenses are recorded in `ContentSources.md`.
- Python Unicode check confirms U+01F0 starts in NFC, casefolding produces a non-NFC sequence, and NFC normalization recomposes it.
- The AI C++ SPSC example compiles as C++11 and transfers 100,000 ordered values between two threads without a failed assertion. This smoke test does not prove all possible concurrent schedules; the ordering explanation was checked against the C++ standard draft.
- Ten game API tests pass on the revised deck, including all-round timer overrides and withholding technical notes, discussion prompts and source links until reveal.
- JSDOM renders all ten rounds on presenter and player pages from API-derived live/reveal snapshots, with monotonic playback timestamps. Checks cover difficulty, neutral context, exact text, image paths, reveal-only engineering notes/references, final 1,750-point score and compatibility with rooms lacking new fields. No JavaScript runtime errors.
- Both new JPEG assets decode and are bundled under 400 KB each; generated image inspected. Source/license and modification notices are included for the camera image. New dependency installation and a database migration are not needed.

### Earlier game and QR checks

- Dependency-file correction: runtime requirements are self-contained, with the previously tested runtime package versions pinned directly. The `-c constraints.txt` include was removed after a reported Vercel parse failure at position 0. All 16 entries parse as standalone requirements, and an offline pip dry run confirms compatibility with the previously verified dependency environment. A successful Vercel rebuild remains to be confirmed.
- Python 3.12 syntax checks for all Python source files.
- JavaScript syntax check with `node --check static/app.js`.
- Ten API test cases in `tests/test_game.py`, using temporary SQLite databases:
  - Full ten-round playthrough, reveal, manual progression and final results.
  - Correct streak progression and a 1,750-point perfect score.
  - Wrong/missing answers reset streaks.
  - Five concurrent attempts to vote produce exactly one accepted vote.
  - Duplicate, stale-round and late votes are rejected.
  - Stale presenter actions and player attempts to control rounds are rejected.
  - Correct answers, explanations and token hashes stay out of live public state.
  - Pseudonym uniqueness, refresh identity, room expiry and configuration guards.
  - Both HTML pages, styles, JavaScript and the current deck's image URLs are served (the two technical images were checked in this update).
- Live DOM integration against a local FastAPI server using the actual delivered HTML and JavaScript:
  - Presenter form creates a room; player form joins with a pseudonym.
  - Presenter start reveals the first question and activates voting.
  - Correct answers are hidden during the timer; vote buttons lock after acceptance.
  - Two real five-second rounds settle through normal polling.
  - Player score changes from 100 to 225, with streaks 1 and 2.
  - Reveal appears on both views; next round waits for a separate presenter start.
  - No JavaScript runtime errors in this integration run.
- Automatic QR checks: presenter-only endpoint, public URL override and compatibility with older room records; the updated presenter draws the Python-generated matrix directly onto a canvas and regenerates it on refresh, without any image-load event.
- QR failure/recovery DOM checks cover a network error, an outdated API response, an aborted request (using an accelerated timeout), and unavailable canvas support. Each shows an explicit error and retry button; retry recovers once the failure is removed.
- Rasterizing the actual frontend canvas draw calls and independently decoding with ZXing matched the exact room link at native resolution, 232 pixels and 210 pixels. These are DOM/raster checks, not a live mobile browser check.
- Independent ZXing decoding of the actual SVG output (rendered to PNG) matched the exact player link for two different rooms at 464, 232 and 210 pixels.
- Human sample source retrieval and bundled image decoding checked. Generated image assets were inspected before inclusion; CPython license included.

## Not verified here

- The new local manager has functional DOM/API checks, not a rendered browser visual review. Actual audio decoding/playback and every uploaded image/audio codec have not been checked on each operating system/phone browser. The guide instructs users to preview and rehearse their own media.

- Audience detection difficulty: levels are editorial, not empirical success-rate measurements. The deck increases technical depth and imitation demands; calibrate its ordering/timers with your audience.
- Live PostgreSQL execution of the question SQL: the fictional snippet is content only. Its explanation was checked against official PostgreSQL locking/UPDATE documentation.

- Full rendered visual/browser QA: local Chromium launch failed in this execution environment. DOM integration does not establish pixel-perfect rendering, actual mobile Safari behavior or accessibility compliance. Rehearse on the intended phone and projector browsers.
- Live Supabase connection, custom-role migration and Vercel deployment: no account credentials were supplied. The PostgreSQL path and deployment instructions use current official documentation, but a real cloud smoke test remains required.
- Production concurrency/load: the 200-player cap is a storage/abuse bound, not a tested capacity guarantee.
- Audio playback: supported by the renderer, but no audio round is bundled.

## Before the event

Run the README's cloud setup, confirm `/api/health` reports Supabase PostgreSQL, and play through from the actual presenter laptop and two phones. Verify the shared link is reachable without a Vercel sign-in, images fit the projected screen, refresh restores the player, the timer closes votes and final standings appear. For a larger audience, rehearse with the intended number of devices on the actual network and hosting plan.
