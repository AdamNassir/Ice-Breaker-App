# Completed update — full supplied LinkedIn passage and identity reveal

## Resulting behavior

- Round 1 displays all four French paragraphs pasted by the presenter, preserving wording and paragraph boundaries. It remains HUMAN, with no company names. The other eight question records are unchanged; nine rounds remain six AI and three HUMAN.
- The supplied image(5).png loads correctly. Its original bytes are bundled as linkedin-profile-source.png; the renderer crops the supplied circular portrait rather than generating a substitute face. Anne GENETET's actual name and this photo are blurred while voting and clear after the server reveals the answer, on both presenter and phone.
- The two 1365 × 1062 post variants have identical body/footer pixels and dimensions. Phone zoom and pan survive the image swap and polling. The public reveal panel remains HUMAN only, with no contextual explanation.
- Optional reveal_media / reveal_alt fields support a local image variant and accessible revealed description. Shared validation rejects unsafe/non-image/missing paths and prevents symlink escapes. The API omits these fields during live voting. Bundled images remain ordinary static assets, not authenticated secret files.
- The question manager edits those optional fields, switches its preview with Show answer notes, and preserves them through save/reload. Script versions are updated on shipped pages so the new renderer loads after redeployment. JSON and Content.py fallback match.

## Install / redeploy

1. Extract the complete ZIP, replacing delivered source while preserving your own .env, secrets and virtual environment.
2. Include both LinkedIn PNG variants, the profile source, both deck files and the updated server/frontend files. Redeploy manually and create a NEW room; existing rooms retain their original snapshots.
3. Restart/reload the local manager. No new runtime dependency. Optional image rebuilding continues to use Pillow; LINKEDIN_POST, LINKEDIN_NAME, LINKEDIN_PORTRAIT and LINKEDIN_PORTRAIT_BOX identify the editable content and framing.

## Validation

44 Python tests and the complete check_project.py frontend/syntax gate pass in the project and a fresh ZIP extraction. Actual API-backed presenter/player DOM checks verify the live/reveal image paths and accessible descriptions, no live field leakage, authoritative timing and unchanged full-game scoring. Manager checks cover preview toggling/save/reload and invalid/missing reveal paths. Gesture checks preserve zoom/pan and polling stability across the image swap. Both images were visually inspected; same dimensions/body/footer and exact supplied portrait-source bytes were checked. Archive manifest/CRC/bytes and exact changed/added paths are verified against the preceding complete ZIP; the other eight round records and unrelated images are unchanged.

## Limits

The post layout is reconstructed around the user-supplied verbatim text and actual supplied photo, not an unmodified original screenshot. HUMAN is the requested public-attribution label; private writing workflow is unverified. Physical phone/projector, native browser and live Vercel/Supabase testing remain unverified as described in Verification.md.

## Modified files since the previous complete ZIP

- `Content.py`
- `ContentSources.md`
- `CreationInstructions.md`
- `HowToAddImages.md`
- `LayoutSources.md`
- `QuestionManager.md`
- `ReadMe.md`
- `UpdateGuide.md`
- `Verification.md`
- `build_question_images.py`
- `main.py`
- `manager_assets/app.js`
- `manager_assets/index.html`
- `question_content.py`
- `questions.json`
- `static/app.js`
- `static/images/sample18.png`
- `static/index.html`
- `static/presenter.html`
- `tests/frontend/game.cjs`
- `tests/frontend/zoom.cjs`
- `tests/run_frontend.py`
- `tests/test_game.py`
- `tests/test_question_manager.py`

## Added files

- `static/images/linkedin-profile-source.png`
- `static/images/sample18-reveal.png`

## Removed files

None.
