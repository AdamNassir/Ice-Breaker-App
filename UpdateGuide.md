# Install the English fun deck

This update replaces the default questions and adds online audio/video playback. No Python package change, Supabase SQL migration or environment-variable change is needed.

## Replace the working app files

1. Stop the local game and question manager. Make a backup of your existing app folder, especially `questions.json` and any uploaded media.
2. Extract this archive to a separate folder. Use the enclosed `Ice_Breaker_Game_App` as the project root: `main.py`, `Content.py` and `questions.json` must be together. Do not accidentally create another nested project root.
3. Copy the files below into the same app folder you actually run/deploy. To use the rebuilt ten-round deck, **replace `questions.json` as well as `Content.py`**. An older `questions.json` takes priority over a newer `Content.py`.
4. Keep your own `.env`, Vercel environment variables, database and uploaded media. Do not rerun `supabase.sql`.
5. Restart locally; reload the manager/presenter with Ctrl+F5 (Windows/Linux) or Cmd+Shift+R (Mac). In the manager, use **Reload saved** to see the ten new questions. **Load starter → Save deck to game** also installs the matching English fallback.
6. Commit the changed files and all new media to your Vercel source repository, push/redeploy, wait for deployment to finish, and open `/presenter`. Create a **new room**: old rooms retain their original deck.

## Exact changed files

| Files | Change |
| --- | --- |
| `Content.py` | New English ten-round fallback deck |
| `main.py` | Exposes playback URLs and clip boundaries in public question state |
| `question_content.py` | Validates HTTPS audio/video links, YouTube IDs and clip times |
| `static/app.js` | Shared audio/video/YouTube rendering on presenter and player screens |
| `static/index.html`, `static/presenter.html` | Loads shared playback script and explains classification |
| `static/imagestyle.css` | Responsive embedded video |
| `manager_assets/index.html`, `manager_assets/app.js`, `manager_assets/style.css` | Local/uploaded or online-link modes, clip times and previews |
| `tests/test_question_manager.py`, `tests/test_game.py` | URL/clip validation, live-state secrecy and bundled-deck checks |
| `ReadMe.md`, `QuestionManager.md`, `HowToAddImages.md`, `ContentSources.md`, `Verification.md`, `static/audio/README.md`, `static/videos/README.md` | Updated instructions, sources and verification |

## New files to include

| Files | Purpose |
| --- | --- |
| `questions.json` | Complete ready-to-play English deck; replaces your old managed deck when copied |
| `static/media.js` | Shared playback code; required by both game and manager |
| `static/images/sample13.jpg` | Napoleon ceremony with hidden guest |
| `static/images/sample14.jpg` | Cat at a mainframe |
| `static/images/sample15.jpg` | Historical motorcycle football |
| `static/images/sample16.jpg` | Historical Tesla double exposure |
| `static/audio/sample17.mp3` | Authentic English Grace Hopper excerpt |
| `ContentSources_Technical.md` | Archived credits for the previous deck |
| `UpdateGuide.md` | These update instructions |

`question_manager.py`, `store.py`, `static/style.css`, `requirements.txt`, `supabase.sql`, and `vercel.json` are unchanged. Previous media/credits remain included so old rooms or backups can still reference them.

## Before projecting

Play both voice clips and both videos using the event laptop's browser and speakers. Three rounds use online sources; they need internet and may be blocked by a venue network, YouTube restrictions or changed source links. Embedded branding can be a clue. If needed, replace those questions with recordings you have permission to host, using the manager.

If a deck error mentions a missing local file, compare its exact path with the new-file table. Copying only the Python or JSON files does not include images/audio. A functioning room, QR code or database does not establish that every media file was deployed.
