# Install the code and aerospace GraphRAG questions

## Changes

- Round 3 replaces the real Trump Truth Social post with a sourced Python download loop and a document-ingestion scenario. The documentation code is unchanged; its formatting is recreated in a zoomable image.
- Round 9 replaces the coffee-rota Teams exchange with an English aerospace GraphRAG internship handover. The validation reply invents aircraft-control features unrelated to the actual pipeline.
- The existing Teams layout, blurred identities and PDF attachment-only presentation remain. The new PDF filename is `GraphRAG_Q3_Technical_Wrapup.pdf`.

## Install

1. Extract the complete ZIP. Replace all modified files below and add `static/images/sample23.png`. Preserve your `.env` and back up custom deck/media files before replacing the default deck.
2. Replace **both** `questions.json` and `Content.py`, plus the image builder and updated Teams PNG.
3. Restart a local server, or commit the changes and redeploy to Vercel. Hard-refresh presenter and player pages.
4. Create a **new room**: rooms store question snapshots, so an existing room keeps its old deck. The question manager should load ten questions without missing-media errors.

No dependency installation or Supabase migration is required. Pillow is needed only if you choose to rebuild the images yourself. The removed Truth Social round's image stays bundled for older rooms.

## Modified files relative to the previous ZIP

- `Content.py`
- `ContentSources.md`
- `HowToAddImages.md`
- `ReadMe.md`
- `UpdateGuide.md`
- `Verification.md`
- `build_question_images.py`
- `questions.json`
- `static/images/sample19.png`

## Added file

- `static/images/sample23.png`

No files were removed. Runtime JavaScript/CSS/Python, dependency files and deployment configuration are unchanged.

## Rehearsal

Start a new room. Confirm round 3 shows the usage scenario and code, not Truth Social. Confirm round 9 shows the GraphRAG handover and new PDF filename. Test pinch zoom on both images. The first reveal should be HUMAN and the Teams reveal AI; no additional source/context text appears for either. Timers, Enter/Next round and final placements should work as before.
