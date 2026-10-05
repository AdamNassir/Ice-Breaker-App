# Add and edit images, audio and video

The easiest method is the **local question manager**: run `python question_manager.py` in your virtual environment, open http://127.0.0.1:8765, click **+ Image**, **+ Audio** or **+ Video**, upload the file and save the deck. Windows/macOS/Linux commands and complete steps are in `QuestionManager.md`.

The manager writes `questions.json` and copies media into the app. For Vercel, commit that JSON and new media, redeploy, then create a **new room**. Existing rooms keep their original questions.

The remaining instructions describe advanced manual file editing. If `questions.json` exists, edit the managed deck through the tool (or edit its JSON): it takes priority over `Content.py`. The `Content.py` examples below apply to the fallback starter when no managed JSON file exists.

## Add an image

1. Copy a JPG, PNG or WebP into `static/images/`. Prefer a landscape image around 1200–1600 pixels wide and under 1 MB for fast phone loading. Use neutral names such as `sample11.jpg`, not `human-photo.jpg` or `ai-answer.png`.
2. In `Content.py`, replace an existing image round or append this dictionary to `ROUNDS`:

```python
{
    "title": "A familiar scene",                 # CHANGE the on-screen title.
    "kind": "image",                            # KEEP this for image rounds.
    "difficulty": 2,                            # CHANGE 1–5; reading/deception level.
    "context": "Inspect this workshop image.",   # CHANGE neutral setup, no origin hint.
    "media": "/static/images/sample11.jpg",      # CHANGE to your exact filename.
    "alt": "A bicycle leaning against a wall.",  # CHANGE accessible description.
    "image_fit": "contain",                      # CHANGE to "cover" to crop.
    "image_position": "center",                  # CHANGE e.g. "50% 30%".
    "answer": "HUMAN",                           # CHANGE to the known origin.
    "explanation": "Describe what actually created this image.",
    "technical_note": "Explain the engineering detail after reveal.",
    "discussion": "Which physical detail influenced your guess?",
    "source": "Photographer name, date, permission or license.",
    "source_url": "https://your-source.example/photo", # Optional, revealed afterward.
},
```

3. Save and restart/redeploy. Create a new room. The round count adjusts automatically. To keep exactly nine rounds, replace a round instead of appending one.
4. Rehearse on the projector and a phone. Confirm the whole image loads and the title/alt text do not reveal its origin.

The path begins with `/static/images/`, not a local path such as `C:\Pictures\photo.jpg`. Match filename case exactly: Vercel/Linux are case-sensitive. `sample11.JPG` and `sample11.jpg` differ. Keep filenames simple with no spaces. Assets are public, so avoid embedding an answer key, identifying metadata that gives away the classification, or confidential source material. Keep attribution in `source`, which the server exposes only at reveal. Preserve source licenses when editing or redistributing assets: the bundled `sample11.jpg` camera photo is by Jguarin under CC BY-SA 4.0; its resized derivative keeps the same license. Current photo/painting assets include `sample13.jpg` (Napoleon cameo), `sample26.jpg` (Michael Jordan’s full-frame 1988 dunk) and `sample16.jpg` (Tesla). `sample15.jpg` is a retained legacy asset. Credits and exact transformations are in ContentSources.md; most previous assets remain available; sample14.jpg has been removed. The motorcycle-football derivative keeps CC BY-SA 3.0 Germany.

## Change image appearance through code

Edit **`static/imagestyle.css`** for every image:

```css
.round-image {
  width: 100%;
  max-height: 420px;     /* CHANGE to 520px for a larger projector image. */
  min-height: 180px;
  object-fit: contain;  /* Entire image, with possible empty space. */
  object-position: center;
  background: #f5f3f4;  /* CHANGE background behind letterboxed images. */
  border-radius: 12px;  /* CHANGE to 0px for square corners. */
}
```

Mobile and large-projector rules are at the bottom of that file. Modify those too if changing device-specific height. Images use `width:100%` so they remain inside the available card.

**Per-round framing takes priority over the global CSS.** All delivered image rounds explicitly use `"image_fit": "contain"` and `"image_position": "center"`. To let global CSS control a round, remove those two keys. To crop only one round:

```python
"image_fit": "cover",
"image_position": "50% 30%",  # Horizontal 50%, vertical 30%; favors the upper part.
```

`contain` shows every pixel. `cover` fills the image element and may crop its edges. To force a specific crop frame, add `aspect-ratio: 3 / 2;` and `height: auto;` to `.round-image`, or set a fixed `height` together with the appropriate responsive height rules. Cropping may hide useful clues, so verify it before the event.

## Crop or resize the actual file

CSS edits affect display only. For permanent pixel edits, create a new sibling file so the original remains available. Optional developer tool:

```bash
python -m pip install Pillow
```

Create `edit_image.py` in the app folder:

```python
from PIL import Image

image = Image.open("static/images/sample11.jpg")  # CHANGE input filename.
# Optional crop box: (left, top, right, bottom), in original pixels.
# image = image.crop((100, 50, 1400, 950))          # CHANGE coordinates, then uncomment.
image.thumbnail((1600, 1600))                     # CHANGE maximum dimensions.
image.convert("RGB").save(
    "static/images/sample11-v2.jpg",              # CHANGE output filename.
    quality=90,
)
```

Run it with your venv's Python, then change the `media` field to `/static/images/sample11-v2.jpg`. Saving without copying EXIF helps remove identifying metadata; check it before sharing. Ordinary resizing/cropping preserves a camera photo's origin for this game's definition. Generative fill or synthetic reconstruction is mixed-origin content: document it explicitly and choose an unambiguous sample instead if you want a strict binary round.

## Add voice recordings

Use MP3 or WAV for broad compatibility. Copy the file into `static/audio/` and replace a text round with:

```python
{
    "title": "Listen carefully",
    "kind": "audio",
    "body": "Listen once, then choose AI or Human.",
    "media": "/static/audio/sample11.mp3",  # CHANGE filename.
    "alt": "A speaker reading a short release note.",
    "answer": "AI",                       # CHANGE to documented voice origin.
    "explanation": "This voice was synthesized from a supplied script.",
    "source": "Voice tool/model and generation date; used with permission.",
},
```

For a human voice, use your own recording or a consenting colleague. Avoid impersonating someone without permission. In an audio round, classify the **voice production**, not who authored the script; explain that before play. Tap Play on the presenter screen after starting the round. Phone playback is optional; headphones prevent echoes. Polling does not replace a live audio element, so it will keep playing. The default deck has no voice rounds. `sample17.mp3` is retained only as a legacy Grace Hopper excerpt.

## Video clips

Use the manager’s **+ Video** button, select an MP4, WebM, OGV, MOV or M4V file up to 25 MB, fill in the editor title and known AI/HUMAN origin, preview it and save the deck. Uploads go to `static/videos/`. Commit the video and `questions.json`, redeploy and create a new room. MP4 with H.264 video and AAC audio is a useful choice for phones. Convert incompatible videos before uploading; the editor does not transcode them. Both presenter and player screens show manual playback controls.

## Link an online recording instead of uploading

The updated manager has **Media source → Online link** for audio/video. Paste a direct HTTPS audio file, direct video file or YouTube video URL and set optional start/end in seconds. See QuestionManager.md for playback and rehearsal details. Example Python dictionary (or corresponding fields in questions.json):

```python
{
    "title": "The robots have better moves than us",
    "kind": "video",
    "media_url": "https://www.youtube.com/watch?v=fn3KWM1kuAw",  # CHANGE URL.
    "media_start": 0,          # CHANGE absolute start in whole seconds.
    "media_end": 18,           # CHANGE absolute end; omit for entire recording.
    "answer": "HUMAN",         # CHANGE to documented footage/voice origin.
    "explanation": "Explain the known origin after the timer ends.",
    "source": "Credit the creator and identify the recording.",
}
```

Do not set both `media` and `media_url`. Uploaded images use `media` only. URLs must be HTTPS; audio needs a direct supported audio file URL, while YouTube is supported as video. A regular article/TED webpage is not a file URL; use the talk's YouTube video link or a recording you may legally host. No download, conversion or voice cloning happens automatically.

The bundled sources/deck and exact install list are in ContentSources.md and UpdateGuide.md. Replace both Content.py and questions.json when adopting the new default; a saved JSON deck takes priority.

The presenter’s timer applies to every round; old question-level seconds values are ignored. Each public question shows `title`, a short neutral `context`, and the text/media. Keep the answer and source out of both public fields. Reveals show AI or HUMAN, plus configured real-photo credits and optional highlights. Extra explanation and discussion notes stay in the editor. The current news articles are AI fiction, with no external source claimed.

## Edit the LinkedIn, Teams, X and code images

The PNGs are already bundled; no image package is needed to play. To rebuild them locally:

```bash
python -m pip install Pillow
python build_question_images.py
```

Use your existing virtual-environment Python on Windows, macOS or Linux. Edit the clearly named `LINKEDIN_POST`, `TEAMS_REQUEST`, `TEAMS_REPLY`, `AI_TWEET` and `AI_SQL` constants in `build_question_images.py`. The `linkedin()`, `teams()`, `tweet()` and `code_card()` functions control layout, colors and font sizes. The verbatim French LinkedIn excerpt is in `LINKEDIN_POST`, with its URL in `LINKEDIN_SOURCE`; inline hashtags are rendered blue. Keep the excerpt unchanged when retaining its source/classification. `linkedin()` uses the new `layout_sources/linkedin-reference.png` crop geometry at 3×, with a summary footer and no extra action row. The French Teams request describes a document-search handover in simple terms; the manager’s reply wrongly describes aircraft operations. The question introduction explicitly identifies that reply as the classification target. Keep identities anonymized and the PDF as an attachment only.

`SOCIAL_NAME_PIXEL_SIZE` and `SOCIAL_AVATAR_PIXEL_SIZE` apply only to legacy anonymized Trump reconstructions, which are not used by the active deck. The current Macron post passes `macron=True` to `tweet()`: name/handle are plain text and `MACRON_PORTRAIT` supplies a real, unblurred face crop. LinkedIn and Teams remain blurred. Rebuilding writes `sample18.png`, `sample19.png`, `sample23.png` and `sample27.png`. The source portrait `profile-source.png` is bundled so the rebuild works locally. Preserve the supplied-picture origin in ContentSources.md. Old `sample21.png` and `sample22.png` remain for older saved room snapshots.

`AI_SQL` contains the original AI-written employee-data query. Keep the PostgreSQL reference's uppercase clauses, lowercase identifiers/functions and four-space clause indentation. `SQL_STYLE_SOURCE` records the formatting reference. `code_card()` renders only the SQL: do not add a prose scenario, title, comment or source clue. The scenario belongs in table/column/filter names. If you replace the code or change its origin, also update the answer/source in both `questions.json` and `Content.py`. Changing the image renderer does not automatically update deck provenance. Pillow is optional for authoring; no new deployment dependency is required.

To change the displayed size on the projector, edit `.presenter-playing .round-image` at the end of `static/imagestyle.css` (currently `max-height: 64vh`). Phone image sizes retain their own limits. Keep `image_fit` set to `contain` to show the full screenshot. Commit the rebuilt PNGs and any deck changes, redeploy, and create a new room.


## Photo credits and reveal circles

For a real photograph, fill **Photo reveal: what it is, date and source** in the local manager's Answer notes and source section. Its JSON field is `image_reveal`. The app shows it only after the deadline, for HUMAN image questions. The existing `source_url` field supplies the View source link. Leave `image_reveal` empty for posts and screenshots so they get no added context.

A circle can be configured in `questions.json` (or in the `Content.py` fallback):

```json
"image_highlight": {"x": 35.5, "y": 43, "radius": 7.5}
```

`x` and `y` are center coordinates in percent of image width and height respectively. `radius` is percent of image width, so the overlay is a true circle at every size. Use `image_fit: "contain"` and centered positioning. For the bundled painting these coordinates surround Inspector Gadget. The SVG circle appears only at reveal; its coordinates are withheld from the live question API. No second image file is needed, and the original painting stays unchanged. The manager preserves this optional configuration on save/import/export; edit the coordinates in JSON when moving the highlight or remove the field to disable it.

Text question paragraphs now use shorter spacing and a smaller presenter font. Change `.stage.text-stage`, `.text-content`, `.text-paragraph`, and `.presenter-playing .text-content` in `static/style.css` to adjust compactness. Podium confetti lives in `celebrate()` in `static/app.js` and the `podium-confetti` CSS animation; it is finite and skipped for reduced-motion preferences.

## Phone zoom and panning

Every image question automatically gets player-only pinch zoom and dragging. Double-tap toggles between 250% and the original view. The **+**, **−** and **Reset** buttons provide the same features without gestures. A focused image also accepts plus/minus, arrow keys to pan and zero to reset.

Zoom and position survive ordinary polling and the answer reveal, and reset for the next question. The reveal circle moves with the image. Scrolling outside the image still scrolls the page; the timer and answer buttons work normally.

Edit `MAX_ZOOM = 6` near the top of **`static/imagezoom.js`** to change the maximum magnification. Edit `.image-viewport`, `.image-zoom-controls` and `.image-zoom-button` in **`static/imagestyle.css`** to change the viewport or controls. Keep the frame and highlight in the same transformed element to preserve circle alignment. No question data or Supabase configuration is needed. The presenter and local manager keep their usual image view.

## Logos and theme

The original PNGs extracted from the supplied document are `static/branding/logiclever.png` and `static/branding/totalenergies.png`. The active LogicLever image is the complete official `logiclever-full.jpg`; the player, presenter, bonus page and local manager reference that image and TotalEnergies directly. Replace the active image files to change the marks; keep the correct width/height attributes and `object-fit: contain`. Do not redraw or recolor them. Adjust `.brand-logos` in `static/style.css` and `manager_assets/style.css` for size or spacing.

Edit `--blue: #1f2ade` and `--red: #e52330` at the top of both stylesheets to change the game theme. The blue is sampled from the supplied LogicLever mark; the red is the requested red UI accent. Existing medal colors belong only to the final podium. `static/imagestyle.css` uses these shared variables for zoom controls. When changing CSS/JS, bump the matching HTML `?v=` suffixes, redeploy and refresh both views.

## Complete opening logos and editable articles

Opening logos are in `static/index.html` and `static/presenter.html`; replace the `src` paths there if you change brands. The original supplied LogicLever PNG clips its own tagline, so these pages use the complete official `static/branding/logiclever-full.jpg`. Keep `height:auto`, `object-fit:contain` and padding on `.brand-logos-hero` in `static/style.css` to avoid clipping. Header/bonus/manager also use the complete source.

The current Macron builder uses the exact supplied profile screenshot `profile-source.png`, crops `(32, 13, 398, 379)` and draws it without blur. Edit **AI_TWEET** in `build_question_images.py`, then run `python build_question_images.py` to rebuild `sample27.png`. The current post is fictional health-AI writing; changing the avatar does not change the writing classification.

For articles, choose **Text → Text presentation → News article** in the manager. First paragraph = headline, next = chapo; separate remaining body paragraphs with blank lines. Both default articles are French. To edit the complete Le Parisien page shell (masthead, navigation, byline, sidebar, related stories and footer), change `static/newsarticle.js`; for its blue/white styling, responsive columns, fonts or scroll height, change `static/newsarticle.css`. Its unchanged vector logo is `static/branding/publication.svg`. The article is native text, not a screenshot. The same renderer previews in the manager and appears on presenter/phones. In JSON/fallback code, set `"text_style": "news"`; omit it or use `"plain"` for normal text. Update `questions.json` and `Content.py` together when changing the bundled starter, redeploy, then create a new room.


LogicLever’s complete original JPEG remains unchanged. `.logo-logiclever{mix-blend-mode:multiply}` in static/style.css and manager_assets/style.css makes its white backdrop blend into the page. Keep the contain sizing and complete tagline. To edit the expanded SQL screenshot, change AI_SQL in build_question_images.py and rebuild with code_card(); its comments, CTEs, joins and FILTER pivot are content, not an external scenario caption. The active default deck contains nine questions; sample20.jpg remains a legacy asset.
