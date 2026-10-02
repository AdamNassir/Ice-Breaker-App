# Local question manager

Run this separate tool on your own computer to edit the game without writing Python. It opens a browser editor at **http://127.0.0.1:8765**. The public game still uses `main.py`; the manager uses `question_manager.py` and is not a public Vercel page.

## Start it

Install Python 3.12 as described in `ReadMe.md`, extract the app, and open a terminal **inside `Ice_Breaker_Game_App`**. The manager uses the existing Python dependencies; Supabase access is not needed to edit questions.

### Windows — PowerShell or Command Prompt

If you have not created the local environment yet:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Start the manager:

```powershell
.\.venv\Scripts\python.exe question_manager.py
```

These commands do not require PowerShell script activation.

### macOS / Linux — Terminal

If you have not created the local environment yet:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Start the manager:

```bash
.venv/bin/python question_manager.py
```

Use a Python 3.12 installation for the virtual environment. Linux users who lack `venv` should follow the distro setup in `ReadMe.md`.

The editor opens automatically. If your browser does not open, visit **http://127.0.0.1:8765**. Keep the terminal running while editing. Press **Ctrl+C** in the terminal to stop; saved files remain on disk.

If port 8765 is busy, add `--port 8767` and use the printed link. To suppress automatic browser opening, add `--no-browser`.

## Add a question

1. Click **Add question**. Choose **Text**, **Code**, **Commit message**, **Image**, or **Voice / audio recording**.
2. Enter a title and select the known **AI** or **HUMAN** origin. The tool records your answer key; it does not infer authorship.
3. Paste text/code, import a plain UTF-8 text file, upload an image/audio file, or select an existing media file.
4. Optionally set the timer (5–120 seconds), difficulty (1–5), accessible description and neutral setup. A blank timer uses the room timer selected by the presenter.
5. Open **Answer notes and source** to add the reveal explanation, credit/source link, technical detail or discussion prompt. These are optional.
6. Inspect **Question preview**. For audio, press Play. Toggle **Show answer notes** to check the reveal.
7. Click **Save deck to game**. All questions are saved together, in their listed order.

For audio, choose AI/HUMAN for how the **voice** was produced, independently of who authored its script. Record with your usual phone/desktop recorder, then upload the recording. This version uploads recordings; it does not capture your microphone inside the editor.

Changes in the editor are a draft until you save the deck. Uploading a file copies it immediately into the app folder; saving the deck links it to the question. Navigating between questions preserves draft edits. Closing/reloading with unsaved changes prompts you before discarding them.

## Edit, reorder and remove

- Click a question in the left list to edit it.
- Use **↑ / ↓** to move the selected question, **Duplicate** for a copy, and **Delete** to remove it from the draft.
- **Start empty** starts a fresh draft. The saved deck remains intact until you save a replacement containing at least one question.
- **Load starter** loads the bundled `Content.py` examples into the draft.
- **Reload saved** discards the draft and reloads the latest file.
- **Download draft** exports a JSON copy, including unfinished questions; importing a draft still requires valid fields before saving.
- **Import JSON** accepts an exported deck or a list of question objects. Referenced images/audio must also be present in the app folder; the JSON does not contain the media bytes.

Deleting a question keeps its media file so other questions, existing rooms or backups can still reference it. The manager does not delete media automatically.

If another tab or code editor changes the saved file, the manager refuses to overwrite that newer version. Download your draft, reload the saved deck, and merge the changes you want to keep.

## Supported content

| Content | How to add it |
| --- | --- |
| Text, incident notes, logs, transcripts, code, commits | Paste or import plain UTF-8 text; up to 50,000 characters per question |
| Images | JPG/JPEG, PNG, WebP, GIF, AVIF, BMP; up to 25 MB per file |
| Voice/audio recordings | MP3, WAV, OGG, Opus, FLAC, M4A, AAC, WebM; up to 25 MB per file |

Browser support determines whether a specific image format/audio codec plays on each phone. Check the preview and rehearse on the target devices. For incompatible image formats such as HEIC/SVG, export a JPG/PNG copy. For incompatible audio, export MP3/WAV. The manager copies files unchanged and gives uploads neutral random filenames, so original filenames do not reveal the answer. It does not convert or synthesize media.

A saved deck can have 1–200 questions and up to 2 MB of question JSON; media files are separate. The game length adjusts automatically. Very long text or recordings need suitable timers and may be awkward for a quick ice breaker.

## Use the deck in a local game

The manager writes **`questions.json` in the app's root**. The game checks that file whenever a **new room** is created; it takes priority over `Content.py`.

Run the game in a second terminal with your usual command:

```bash
python -m uvicorn main:app --reload
```

Open **http://127.0.0.1:8000/presenter** and create a new room. Saving a new deck does not alter an existing room. If the local game is already running, a restart is not required for a changed `questions.json`.

If `questions.json` does not exist, the game uses the bundled `Content.py` starter deck. The manager creates `questions.json` on the first successful save. Invalid JSON or missing referenced media stops new room creation with a clear error rather than silently substituting another deck.

## Use the deck on Vercel

Editing locally does not directly change a deployed Vercel game.

1. Save the deck in the manager.
2. Commit **`questions.json`** and any new files in **`static/images/`** or **`static/audio/`** to the same source repository used by Vercel. Keep any required attribution/license files with the source.
3. Push your changes and let Vercel deploy, or redeploy using your usual workflow.
4. Open the deployment's `/presenter` page and create a **new room**.

For the first installation of this manager update, replace **`main.py`**, add **`question_content.py`**, **`question_manager.py`**, and the **`manager_assets/`** folder, and update `.gitignore` plus the documentation/tests from this archive. You can keep your existing `Content.py` questions as the starter deck. No Python dependency update or Supabase SQL migration is required. The manager is separate from the public game's routes.

After that first deployment, routine question edits only require the changed `questions.json`, media and relevant credit/license files. Do not commit `.env`, virtual environments, SQLite files or the automatic backup folder; the supplied `.gitignore` handles these.

## Backups and recovery

Every successful save first keeps the previous deck in **`.question-manager-backups/`**, then atomically replaces `questions.json`. The first backup contains the starter deck. Backups are local and excluded from Git.

To restore, click **Import JSON**, select a backup file and save the restored deck. Alternatively, copy a known-good backup over `questions.json` while the manager is stopped, then restart it. A malformed external edit is retained in its backup when repaired; that malformed copy itself will not be a valid import.

## Files you will edit through the tool

```text
Ice_Breaker_Game_App/
  questions.json                    Created on first save; deploy this file
  static/images/sample_<random>.*   Added when you upload an image
  static/audio/sample_<random>.*    Added when you upload a recording
  .question-manager-backups/        Previous decks, kept locally
```
