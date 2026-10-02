# Add and edit images (and audio)

The easiest method is the **local question manager**: run `python question_manager.py` in your virtual environment, open http://127.0.0.1:8765, choose Image or Voice/audio, upload the file and save the deck. Windows/macOS/Linux commands and complete steps are in `QuestionManager.md`.

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
    "seconds": 30,                               # Optional per-round timer.
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

The path begins with `/static/images/`, not a local path such as `C:\Pictures\photo.jpg`. Match filename case exactly: Vercel/Linux are case-sensitive. `sample11.JPG` and `sample11.jpg` differ. Keep filenames simple with no spaces. Assets are public, so avoid embedding an answer key, identifying metadata that gives away the classification, or confidential source material. Keep attribution in `source`, which the server exposes only at reveal. Preserve source licenses when editing or redistributing assets: the bundled `sample11.jpg` camera photo is by Jguarin under CC BY-SA 4.0; its resized derivative keeps the same license. The default technical image rounds are `sample11.jpg` and `sample12.jpg`; the four older assets remain optional.

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
    "seconds": 45,                        # Allow time for playback and voting.
    "answer": "AI",                       # CHANGE to documented voice origin.
    "explanation": "This voice was synthesized from a supplied script.",
    "source": "Voice tool/model and generation date; used with permission.",
},
```

For a human voice, use your own recording or a consenting colleague. Avoid impersonating someone without permission. In an audio round, classify the **voice production**, not who authored the script; explain that before play. Tap Play on the presenter screen after starting the round. Phone playback is optional; headphones prevent echoes. Polling does not replace a live audio element, so it will keep playing. No audio asset is included in the default ten rounds.
