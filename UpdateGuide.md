# Install the Trump identity pixelation update

Both Trump cards now use coarse pixelation on the profile picture, name and handle. Names and handles are no longer readable. Their writing and layouts are unchanged; the previous ten-round deck and phone-only bonus remain included.

## Install

Replace the modified files below, commit and redeploy, then hard-refresh presenter and phone pages to load the updated images. Keep your `.env` and deployment settings. No new dependencies or database migration are needed. `questions.json` and its matching `Content.py` fallback are both included.

## Modified files relative to the previous ZIP

- `build_question_images.py`
- `static/images/sample21.png`
- `static/images/sample22.png`
- `questions.json`
- `Content.py`
- `ReadMe.md`
- `HowToAddImages.md`
- `ContentSources.md`
- `Verification.md`
- `UpdateGuide.md`

No files were added or removed in this update. The cat image remains excluded, as in the previous ZIP.

## Customize pixelation

In `build_question_images.py`, change `SOCIAL_NAME_PIXEL_SIZE` (currently 24) and `SOCIAL_AVATAR_PIXEL_SIZE` (currently 20). Larger values hide more detail. Rebuild with `python build_question_images.py` and inspect both Trump cards before deploying. The current sizes replace letter shapes with coarse solid blocks. LinkedIn and Teams retain their previous appearance.
