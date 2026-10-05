# Completed update — news photographs, believable articles and Teams message direction

## Resulting behavior

- The complete news website now has six photographic neighbour cards: three actual recent Le Parisien photographs, repeated in the sidebar and related row, replacing colour placeholders. The original JPEGs are bundled locally without image edits or remote hotlinks. Source articles, dates, image URLs and observed credits are recorded in LayoutSources.md.
- Replaced La rédaction with the requested named mock bylines: Sébastien Lernould for the economy article and Dominique Sévérac for the sports article, both verified on their author pages. Decorative publication timestamps complete the arrangement. Neither journalist wrote/published the fictional central story; this is explicit in private provenance.
- Rewrote both French AI articles more plausibly: a wrong bitcoin price on one platform with a brief suspension/review; a partner’s accidentally published Ballon d’Or webpage, with prepared pages for several candidates as an alternative explanation. No trophy-by-mail, private-mail-access or delivery-tracker premise remains.
- Teams now shows Adam’s outgoing document submission on the right in light blue and the incoming manager response on the left in light grey. Adam Nassir is the actual supplied sender name and is blurred. The manager remains fictional/anonymized, the messages are fictional and unchanged, and the PDF stays closed.
- Includes the pending prompt cleanup across all nine questions: only the classification target remains. No read/look/inspect commands appear. The standalone legacy Read the French post prompt is also cleaned when decks or existing room snapshots are displayed. Custom part-specific classification targets remain intact.
- The deck still has nine rounds with seven AI/two HUMAN; scoring, timer, QR, Next/Enter, phone zoom, final placements/confetti and phone-only bonus are preserved. JSON and Content.py fallback remain equivalent.

## Install / redeploy

1. Replace delivered app source with the complete ZIP, preserving your own .env, virtual environment and secrets.
2. Redeploy normally and create a NEW room to load the revised article writing. Existing room snapshots intentionally keep their saved content; recognized older viewing instructions are normalized for display.
3. Include the new static/news directory with all three JPEGs. Updated HTML cache keys load the new shared news JS/CSS on player, presenter and local manager.
4. Restart/reload the local question manager. No runtime dependency changes. To rebuild the Teams image later, install optional Pillow and run the documented build_question_images.py authoring script; the deployed app only serves its bundled PNG.

## Validation

43 Python tests and the complete check_project.py gate pass. HTTP-loaded player/presenter/manager checks verify six local JPEG cards, actual responses/bytes, cover framing with no inherited minimum height, both named bylines and removal of La rédaction. Hostile question markup remains literal text; only fixed trusted logo/photo assets are created. Legacy prompt normalization preserves custom targets and stored room snapshots. Full nine-round API/frontend checks cover timing, scoring, Next/Enter, zoom, ranking/confetti, bonus/workflow, manager save/reload and upload. The rebuilt Teams PNG and all three downloaded news photographs were visually inspected. JSON/fallback match. Complete archive manifest/bytes are compared with the last delivered ZIP and a fresh extraction passes the same full gate.

## Limits

Native Chromium rendering, pixel-identical layout matching, physical phone/projector testing and live Vercel/Supabase deployment are not claimed. The existing viewport/font matching limitation remains documented in LayoutSources.md and Verification.md. Editorial photographs are sourced/credited; no public-domain or Creative Commons licence is claimed. The article bodies, borrowed-name bylines and displayed timestamps are fictional quiz presentation, not reports published by the outlet.

## Modified files since the last delivered complete ZIP

- `Content.py`
- `ContentSources.md`
- `CreationInstructions.md`
- `LayoutSources.md`
- `QuestionManager.md`
- `ReadMe.md`
- `UpdateGuide.md`
- `Verification.md`
- `build_question_images.py`
- `main.py`
- `manager_assets/index.html`
- `question_content.py`
- `questions.json`
- `static/images/sample19.png`
- `static/index.html`
- `static/newsarticle.css`
- `static/newsarticle.js`
- `static/presenter.html`
- `tests/frontend/game.cjs`
- `tests/frontend/resources.cjs`
- `tests/run_frontend.py`
- `tests/test_game.py`

## Added files

- `static/news/ai.jpg`
- `static/news/football.jpg`
- `static/news/housing.jpg`

## Removed files

None.
