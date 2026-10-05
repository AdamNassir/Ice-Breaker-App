# Completed update — logos, blue/red theme and revised questions

## Resulting behavior

- Both original supplied logos, LogicLever and TotalEnergies, appear in the player/presenter entry and game header, standalone bonus page and local question manager. Presenter final results retain their placements-only layout.
- Public game and local manager use blue and red with white/neutral backgrounds. The logo pixels are not recolored. Metal colors remain only in final tournament decoration.
- Every question shows an English title and short neutral introduction above its content. The QR lobby has no question yet, and presenter final results contain no round title or intro.
- Both textual questions are replaced with plausible AI-written fictional news articles: a Bitcoin price-dashboard incident and a Ballon d’Or delivery-tracker leak. They are original quiz fiction, not genuine reporting.
- A real Michael Jordan dunk replaces the motorbike-football round; subject/date/photographer/source appear only at reveal. The active Trump post is replaced by an AI-written French Macron parody with an unblurred real portrait, name and handle. It is not a genuine statement or account screenshot.
- The Teams exchange is in French with less technical wording. The intern asks for validation of a document-search handover; the manager mistakes it for aircraft operations. The introduction explicitly asks players to classify the manager’s reply only. Identities stay anonymized and the PDF remains an attachment, without its interior.
- Ten rounds remain: eight images/two texts, seven AI/three HUMAN. No audio/video questions. Both deck files match; private origins/source notes remain hidden while voting.

## Install and redeploy

1. Extract the complete ZIP into the app source folder, replacing the modified/added files below. Preserve your own .env, virtual environment and deployment secrets. To adopt these questions, replace both questions.json and Content.py; your existing saved JSON deck otherwise takes priority over the fallback.
2. Include the complete static/branding directory, sample24.jpg, sample25.png and macron-profile-source.jpg, plus the rebuilt sample19.png. Keep the unchanged media supplied with this complete archive as well.
3. Stop/restart the local question manager and hard-refresh it (Ctrl+F5 on Windows). The title and short introduction fields control the public heading; private explanations/sources remain answer notes.
4. Redeploy the updated source to Vercel through your usual workflow, then refresh presenter and phones. Updated asset query versions avoid older cached CSS/JS. No new production dependency or Supabase migration is needed.
5. Create a NEW room: existing rooms keep their earlier question snapshots. Rehearse the QR, questions and selected duration on your projector and phone. Optional image rebuilds use python -m pip install Pillow, then python build_question_images.py.

## Validation

42 Python tests and the complete check_project.py gate pass. Frontend checks cover exact titles/intros, blue/red tokens/logos, all ten actual API question states, timer/source secrecy, manager saves/uploads, zoom/pan/reveal alignment, Next/Enter, rankings/confetti and bonus/workflow persistence. Both rebuilt French screenshots were visually inspected. Logo byte identities and Jordan source-image checksum were verified. The full ZIP is freshly extracted, byte-compared and checked with the same gate. Physical phone/projector, live Vercel/Supabase and authenticated CLI integration were not tested here; see Verification.md.

## Modified files relative to the previous ZIP

- `Content.py`
- `ContentSources.md`
- `CreationInstructions.md`
- `HowToAddImages.md`
- `QuestionManager.md`
- `ReadMe.md`
- `UpdateGuide.md`
- `Verification.md`
- `build_question_images.py`
- `manager_assets/index.html`
- `manager_assets/style.css`
- `questions.json`
- `static/app.js`
- `static/bonus.html`
- `static/images/sample19.png`
- `static/imagestyle.css`
- `static/index.html`
- `static/presenter.html`
- `static/style.css`
- `tests/frontend/game.cjs`
- `tests/run_frontend.py`
- `tests/test_game.py`

## Added files

- `static/branding/logiclever.png`
- `static/branding/totalenergies.png`
- `static/images/macron-profile-source.jpg`
- `static/images/sample24.jpg`
- `static/images/sample25.png`

## Removed files

None. Older images are retained for previous room snapshots/custom decks, but are not active questions.
