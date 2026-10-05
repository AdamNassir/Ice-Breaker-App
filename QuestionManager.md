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

1. Click **Add question**. Choose **Text**, **Code**, **Commit message**, **Image**, **Voice / audio recording**, or **Video clip**. For media, the visible **+ Image**, **+ Audio**, and **+ Video** buttons add a question and open its upload controls directly.
2. Enter a title and select the known **AI** or **HUMAN** origin. The tool records your answer key; it does not infer authorship.
3. Paste/import text, upload an image/audio/video file or select an existing media file. For audio/video you can instead choose **Online link** and paste a direct HTTPS file URL; video also accepts YouTube watch/share links. Optionally enter clip start/end in seconds.
4. Add an accessible description and any private setup/difficulty notes. The presenter’s timer applies to every round; stored question timers are ignored. Titles and introductions are retained for editing but are hidden in the public game.
5. Open **Answer notes and source** to keep private explanations, credit/source links, technical details or discussion prompts. The game reveals AI or HUMAN. For a real photograph, fill **Photo reveal: what it is, date and source** to add a concise public caption at reveal; Source link adds the photo-source link. Leave that caption empty for social posts. Other explanation/discussion fields remain editor notes. These are optional.
6. Inspect **Question preview**. For audio/video, press Play; playback starts when you choose it. Toggle **Show answer notes** to check the reveal.
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
- **Import JSON** accepts an exported deck or a list of question objects. Referenced images/audio/video must also be present in the app folder; the JSON does not contain the media bytes.

Deleting a question keeps its media file so other questions, existing rooms or backups can still reference it. The manager does not delete media automatically.

If another tab or code editor changes the saved file, the manager refuses to overwrite that newer version. Download your draft, reload the saved deck, and merge the changes you want to keep.

## Supported content

| Content | How to add it |
| --- | --- |
| Text, incident notes, logs, transcripts, code, commits | Paste or import plain UTF-8 text; up to 50,000 characters per question |
| Images | JPG/JPEG, PNG, WebP, GIF, AVIF, BMP; up to 25 MB per file |
| Voice/audio recordings | MP3, WAV, OGG, Opus, FLAC, M4A, AAC, WebM; up to 25 MB per file |
| Video clips | MP4, WebM, OGV, MOV, M4V; up to 25 MB per file |

Browser support determines whether a specific image format or audio/video codec plays on each phone. Check the preview and rehearse on the target devices. For incompatible image formats such as HEIC/SVG, export a JPG/PNG copy. For incompatible audio, export MP3/WAV. For video, MP4 with H.264 video and AAC audio is a useful phone-compatible choice; convert AVI/MKV and incompatible MOV files to that format. Files remain unchanged, so an accepted extension does not guarantee its codec will play on every device. The manager copies files unchanged and gives uploads neutral random filenames, so original filenames do not reveal the answer. It does not convert or synthesize media.

A saved deck can have 1–200 questions and up to 2 MB of question JSON; media files are separate. The game length adjusts automatically. Very long text or recordings need suitable timers and may be awkward for a quick ice breaker.

## Use the deck in a local game

The manager writes **`questions.json` in the app's root**. The game checks that file whenever a **new room** is created; it takes priority over `Content.py`.

Run the game in a second terminal with your usual command:

```bash
python -m uvicorn main:app --reload
```

Open **http://127.0.0.1:8000/presenter** and create a new room. Saving a new deck does not alter an existing room. If the local game is already running, a restart is not required for a changed `questions.json`.

If `questions.json` does not exist, the game uses the bundled `Content.py` starter deck. This archive already contains the English `questions.json`; the manager replaces it when you save. Invalid JSON or missing referenced media stops new room creation with a clear error rather than silently substituting another deck.

## Use the deck on Vercel

Editing locally does not directly change a deployed Vercel game.

1. Save the deck in the manager.
2. Commit **`questions.json`** and any new files in **`static/images/`** or **`static/audio/`** or **`static/videos/`** to the same source repository used by Vercel. Keep any required attribution/license files with the source.
3. Push your changes and let Vercel deploy, or redeploy using your usual workflow.
4. Open the deployment's `/presenter` page and create a **new room**.

For the first installation of this manager update, replace **`main.py`**, add **`question_content.py`**, **`question_manager.py`**, and the **`manager_assets/`** folder, and update `.gitignore` plus the documentation/tests from this archive. You can keep your existing `Content.py` questions as the starter deck. No Python dependency update or Supabase SQL migration is required. The manager is separate from the public game's routes.

After that first deployment, routine question edits only require the changed `questions.json`, media and relevant credit/license files. Do not commit `.env`, virtual environments, SQLite files or the automatic backup folder; the supplied `.gitignore` handles these.

## Backups and recovery

If an image, recording or video is missing, the manager still opens the questions and shows a warning with the question number and file path. Select that question and upload a replacement, choose an existing file, or delete the question. Then click **Save deck to game**. Saving and creating game rooms still require all referenced media to exist. You can also restore the missing file to the exact folder and filename shown in the warning, then choose **Reload saved**. Copy the complete `static/` folder when moving the app between computers; copying Python files alone does not copy the media.

Every successful save first keeps the previous deck in **`.question-manager-backups/`**, then atomically replaces `questions.json`. The first backup contains the starter deck. Backups are local and excluded from Git.

To restore, click **Import JSON**, select a backup file and save the restored deck. Alternatively, copy a known-good backup over `questions.json` while the manager is stopped, then restart it. A malformed external edit is retained in its backup when repaired; that malformed copy itself will not be a valid import.

## Files you will edit through the tool

```text
Ice_Breaker_Game_App/
  questions.json                    Bundled deck, updated on save; deploy this file
  static/images/sample_<random>.*   Added when you upload an image
  static/audio/sample_<random>.*    Added when you upload a recording
  static/videos/sample_<random>.*   Added when you upload a video
  .question-manager-backups/        Previous decks, kept locally
```

## Installing the media/video update

Stop the manager with Ctrl+C. Replace `question_manager.py`, `question_content.py`, `main.py`, the complete `manager_assets/` folder, `static/app.js`, and `static/imagestyle.css`. Keep your existing `Content.py`, `questions.json` and uploaded media. Restart the manager and refresh the browser (Ctrl+F5 on Windows). You should see **+ Image**, **+ Audio**, and **+ Video** beneath Add question. If those buttons are absent, check that the updated `manager_assets` folder is inside the same app folder as the `question_manager.py` you run. No dependency installation or database migration is required for this update. Redeploy the updated game files to use video on Vercel.

## Presenter says Question deck cannot load

The presenter error identifies the source deck, question number and missing media path or invalid field. The message remains visible until you retry creating a room.

- If it says **questions.json is absent**, the game is using the `Content.py` starter. Click **Save deck to game** in the manager and copy/commit the resulting `questions.json` into the app root used by the game.
- If it says a media file is missing, copy that exact referenced file into the corresponding `static/images`, `static/audio` or `static/videos` folder in the game project. Use the exact filename and letter case; Vercel paths are case-sensitive. A JSON deck does not contain the media bytes.
- If it says the video kind is invalid, the game server has older `question_content.py` code. Update that module and `main.py`, restart the local game or redeploy Vercel.
- If JSON is invalid or a field needs repair, reopen the local manager, fix the deck and save it again.

For Vercel, committing only the Python files is insufficient for a custom deck: commit `questions.json` and all its referenced media too, push and wait for the deployment to finish, then create a new room. Updating the local manager does not change the hosted game automatically.

## Online audio, YouTube and clip boundaries

Choose **+ Audio** or **+ Video**, then **Media source → Online link**. Enter:

- Audio: a direct HTTPS URL ending in a supported file extension, such as `.mp3` or `.wav`.
- Video: a direct HTTPS `.mp4`/other supported file URL, or a YouTube watch/share URL. For example `https://www.youtube.com/watch?v=fn3KWM1kuAw`.

A YouTube page is not a direct audio file. Use Video for a YouTube lecture/talk; you may tell participants to judge its voice if the framing and answer notes make that clear. This tool does not extract/download YouTube audio. Ordinary webpage URLs are not media files. Uploaded images remain local files.

**Clip start/end** are absolute whole seconds from the recording's beginning. To play 1:10 through 1:20, use start `70`, end `80`. Blank start means zero; blank end means play to the recording's end. End must be after start. Choose the presenter’s game timer to leave time to listen/watch and vote. Press Play in the preview; playback is manual in both game screens too. For HTML audio/video the player seeks to start and pauses at end; YouTube receives those boundaries as embed parameters. Controls can expose the original recording beyond your excerpt, so use a separately trimmed upload if a strict excerpt is required.

Online links remain links in the saved deck; they are not copied to `static/`. Playback comes directly from that host and requires internet. URLs are validated for format, not continuously monitored for availability. External servers, browser codecs and embedding permissions determine playback. Source branding or titles may provide clues. Rehearse before hosting and keep attribution in answer notes.

Switch to **Local file / upload** to use your own recording instead. Uploading a new file clears the question's online link. Store the known origin and source yourself; the tool does not guess whether content was generated.

## Install this English fun deck update

Follow **UpdateGuide.md** for the current exact replacement list. In particular copy **static/media.js**, the updated HTML files, both deck files and all five new local assets. Earlier installation sections above describe previous versions; use UpdateGuide.md for this archive. Replace the older questions.json to use the new questions, or back it up and choose Load starter → Save deck to game. Existing rooms keep their previous deck.


The optional `image_highlight` JSON object is preserved when saving or exporting questions. It holds reveal-only circle coordinates; edit those in `questions.json`, then Reload saved. See HowToAddImages.md for the example and units. Existing decks without either new image field continue to load.


## Source links for real text at reveal

Round 5 keeps its four RFC credits in the optional `reveal_sources` list. The manager preserves this list through saving, importing and exporting; edit it in `questions.json`, then choose **Reload saved**. Each entry has `label` and an HTTPS `url`. For example:

```json
"reveal_sources": [
  {"label": "RFC 1149 — April 1, 1990", "url": "https://www.rfc-editor.org/rfc/rfc1149.html"}
]
```

Up to eight links are allowed. Labels can include source names and publication dates. The game displays this list only for HUMAN text questions after the deadline, on presenter and phones. It is excluded from live question payloads. Leave it empty for social posts and AI text. Private **Source** and **Source link** notes do not automatically become public text credits. For manual edits, keep `Content.py` consistent with the JSON fallback when distributing the starter deck.
