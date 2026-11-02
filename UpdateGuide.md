# IceBreaker: LogicLever branding, midnight mode and video-first countdown

## Changes in this version

- Removed TotalEnergies logo from all game and local Question Manager pages, and removed the unused PNG from the project.
- Centered the supplied LogicLever logo on headers and opening screens. Its original black text is always displayed over a light surface, including in midnight mode.
- Added **Midnight mode / Light mode** toggle to presenter, player, standalone bonus and local Question Manager. It uses browser `localStorage` and persists on each site origin. The separate local manager and deployed Vercel site have independent preferences.
- Removed the literal **THE CREW** section title while keeping individual team roster names.
- Added a **watching** phase for video questions: the presenter starts the round, video plays, and server-authoritative voting timer starts only when the presenter player reports `ended`. For YouTube, the supported IFrame API reports the same event. If autoplay or event detection fails, presenter can click **Video cannot finish? Start voting** once the clip has actually finished.
- Refreshed the local Question Manager's help text to describe optional context and video-timer behavior. No change to the shared `questions.json` schema.

## GitHub + Vercel deployment

1. Unzip the updated project into your **existing GitHub working copy**. Preserve your `.git` directory, `.env`, local database and any newer files or media not supplied here. Review changes before committing; don't replace production secrets.
2. Commit source files and any intended `questions.json` and `static` media edits. **Do not** commit `.env`, a local `game.sqlite3`, `.venv`, `node_modules`, `.agent`, caches or question-manager backups.
3. Push to the branch connected to your Vercel production deployment and wait for the deployment to complete. No new dependency, SQL migration or change to `vercel.json` is required.
4. Check `<YOUR_DEPLOYMENT>/api/health` and open `/presenter`. Create a **new** room and test both phone and presenter screens. Try the midnight toggle and verify that team cards no longer say THE CREW.
5. Add a short video question locally if you want to validate the new playback-before-timer behavior, then save `questions.json`, push and deploy, create another new room and rehearse. **The bundled nine-question deck contains no videos.** Test both locally uploaded MP4 and a YouTube link on target devices.

The public game is run by `main.py`; the Question Manager in `question_manager.py` runs **only on your computer**, not on Vercel. The manager saves `questions.json` in the same local folder. After editing a question, use **Save deck to game**, commit/push `questions.json` (and new media) to GitHub, allow Vercel to redeploy, and open a **new** room. A live room retains its already loaded question snapshot.

## Question content and limits

The manager and game already use the same `Question` model in `question_content.py`, so saved questions, optional context, sources and media are read by `main.py` when a new room is created. The editor supports text/notes/logs/transcripts/code/commit messages (UTF-8 text, 50,000 characters), image uploads (JPG, PNG, WebP, GIF, AVIF, BMP), audio uploads or direct HTTPS media URLs, and video uploads/direct HTTPS video URLs/YouTube watch or share URLs. Its media upload size limit is **25 MB per file**. Optional `context` is visible with every question type (max **2,000 characters**). A title, known AI/HUMAN answer and valid body or media source are required; the system does not automatically classify the question.

**Not arbitrary file formats:** PDF, DOCX, PPTX, HTML websites as navigable pages, and arbitrary social links cannot be inserted as playable question media without preparing them first. Convert to text, an image, or compatible audio/video. A YouTube URL must point to a supported video. Check browser codec and embedding restrictions. Clip trimming works on supported HTML media and YouTube.

The managed deck takes precedence over `Content.py`. Edits in `Content.py` do not override an existing `questions.json`. No live, bidirectional syncing with GitHub or Supabase is implemented: GitHub/Vercel deployment is the update mechanism, not a collaboration API.

## Testing

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m unittest discover -s tests -p 'test_game.py' -v
python -m unittest discover -s tests -p 'test_question_manager.py' -v
npm --prefix tests/frontend ci
python tests/run_frontend.py
```

The frontend script tests UI code against the actual local API, including a simulated video-end transition. This is separate from hands-on YouTube/autoplay verification on physical devices. Local SQLite is sufficient for tests, while Vercel needs Supabase `DATABASE_URL` and a presenter password.
