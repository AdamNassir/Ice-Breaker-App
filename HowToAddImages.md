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

3. Save and restart/redeploy. Create a new room. The round count adjusts automatically. To keep exactly ten rounds, replace a round instead of appending one.
4. Rehearse on the projector and a phone. Confirm the whole image loads and the title/alt text do not reveal its origin.

The path begins with `/static/images/`, not a local path such as `C:\Pictures\photo.jpg`. Match filename case exactly: Vercel/Linux are case-sensitive. `sample11.JPG` and `sample11.jpg` differ. Keep filenames simple with no spaces. Assets are public, so avoid embedding an answer key, identifying metadata that gives away the classification, or confidential source material. Keep attribution in `source`, which the server exposes only at reveal. Preserve source licenses when editing or redistributing assets: the bundled `sample11.jpg` camera photo is by Jguarin under CC BY-SA 4.0; its resized derivative keeps the same license. The current images are `sample13.jpg` (Napoleon cameo), `sample15.jpg` (motorcycle football) and `sample16.jpg` (Tesla). Credits and exact transformations are in ContentSources.md; most previous assets remain available; sample14.jpg has been removed. The motorcycle-football derivative keeps CC BY-SA 3.0 Germany.

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

For a human voice, use your own recording or a consenting colleague. Avoid impersonating someone without permission. In an audio round, classify the **voice production**, not who authored the script; explain that before play. Tap Play on the presenter screen after starting the round. Phone playback is optional; headphones prevent echoes. Polling does not replace a live audio element, so it will keep playing. The default deck includes a local Grace Hopper excerpt, sample17.mp3, and a linked synthesized voice example.

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

The bundled sources/English deck and exact install list are in ContentSources.md and UpdateGuide.md. Replace both Content.py and questions.json when adopting the new default; a saved JSON deck takes priority.

The presenter’s timer now applies to every round. Any older question-level seconds value is ignored. In the public game, only text/media content is shown, and the reveal is AI or HUMAN, with a short caption/source link for configured real photographs and an optional image highlight. Social posts receive no added context. Titles, context, explanations and source notes remain available in the editor and these instructions.

## Edit the LinkedIn, Teams and tweet screenshots

The PNGs are already bundled; no image package is needed to play. To rebuild them locally:

```bash
python -m pip install Pillow
python build_question_images.py
```

Use your existing virtual-environment Python on Windows, macOS or Linux. Edit the clearly named `LINKEDIN_POST`, `TEAMS_REQUEST`, `TEAMS_REPLY`, and `AI_TWEET` constants in `build_question_images.py`. The `linkedin()`, `teams()`, and `tweet()` functions control positions, dimensions, colors and font sizes. `SOCIAL_NAME_PIXEL_SIZE = 24` and `SOCIAL_AVATAR_PIXEL_SIZE = 20` control coarse pixelation on the two Trump cards: larger blocks hide more detail. `pixelate()` averages away the original details and scales back up with solid nearest-neighbor pixels. `blurred_label()` and `avatar()` accept `pixel_size` for these cards; LinkedIn and Teams retain their existing Gaussian blur. Rebuilding overwrites `static/images/sample18.png`, `sample19.png`, `sample21.png`, and `sample22.png`. Inspect all four for text overflow after editing. `GENUINE_TWEET` preserves a verified May 16, 2025 Truth Social post: keep its wording intact to retain the HUMAN label, or replace it with another verified human-written post and update its source. Edit `AI_TWEET` for the fictional parody; if the text origin changes, update its answer too. Do not change `requirements.txt`; Pillow is optional for this authoring tool only.

To change the displayed size on the projector, edit `.presenter-playing .round-image` at the end of `static/imagestyle.css` (currently `max-height: 72vh`). Phone image sizes retain their own limits. Keep `image_fit` set to `contain` to show the full screenshot. Commit the rebuilt PNGs and any deck changes, redeploy, and create a new room.


## Photo credits and reveal circles

For a real photograph, fill **Photo reveal: what it is, date and source** in the local manager's Answer notes and source section. Its JSON field is `image_reveal`. The app shows it only after the deadline, for HUMAN image questions. The existing `source_url` field supplies the View source link. Leave `image_reveal` empty for posts and screenshots so they get no added context.

A circle can be configured in `questions.json` (or in the `Content.py` fallback):

```json
"image_highlight": {"x": 35.5, "y": 43, "radius": 7.5}
```

`x` and `y` are center coordinates in percent of image width and height respectively. `radius` is percent of image width, so the overlay is a true circle at every size. Use `image_fit: "contain"` and centered positioning. For the bundled painting these coordinates surround Inspector Gadget. The SVG circle appears only at reveal; its coordinates are withheld from the live question API. No second image file is needed, and the original painting stays unchanged. The manager preserves this optional configuration on save/import/export; edit the coordinates in JSON when moving the highlight or remove the field to disable it.

Text question paragraphs now use shorter spacing and a smaller presenter font. Change `.stage.text-stage`, `.text-content`, `.text-paragraph`, and `.presenter-playing .text-content` in `static/style.css` to adjust compactness. Podium confetti lives in `celebrate()` in `static/app.js` and the `podium-confetti` CSS animation; it is finite and skipped for reduced-motion preferences.
