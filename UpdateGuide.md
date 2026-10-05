# Completed update — RFC reveal sources and implied SQL scenario

## Resulting behaviour

- Round 5 still uses the original April Fools excerpts. Its HUMAN reveal now shows all four RFC source links and publication dates on both presenter and phone screens. Sources remain hidden while voting. No explanation/discussion paragraphs are added.
- Round 3 replaces the human Requests download example with original AI-written SQL for active employee headcounts and average salaries by department. The scenario is implied by table, column and filter names. Only SQL appears in the image; no scenario paragraph, title, comments or source clues.
- SQL formatting follows the official PostgreSQL Aggregate Functions tutorial: uppercase clauses, lowercase identifiers/functions and four-space clause indentation. The reference URL and provenance stay in private author notes. The reveal is AI. The deck now has six AI and four HUMAN questions, still ten rounds.
- Both deck files match. Optional reveal-source metadata is validated, kept out of live payloads and preserved by the local manager. See QuestionManager.md to edit its JSON list. Other questions and images are unchanged.

## Install and verify

1. Extract this complete ZIP and replace the modified files below in your repository. Preserve your local .env. Back up a custom deck before replacing questions.json/Content.py; the supplied files contain this updated default deck.
2. Commit the changed deck, source, frontend and sample23.png files and redeploy to Vercel. No new pip dependency or Supabase migration is needed. Restart local FastAPI/question-manager processes to load the new parser/deck.
3. Hard-refresh presenter/player pages. Create a new room: already-created rooms keep their earlier deck snapshot. Use the new SQL image with the new deck, not an older room's code question.
4. Round 3 should show SQL alone and reveal AI. Round 5 should show HUMAN plus four RFC links/dates only once its countdown ends. Rehearse on a phone and projector after deployment.
5. For a later change, replace this report with the request and save UpdateGuide.md. A running agent reads it, implements/tests, then replaces completed requests with a report for human review. No deployed file watcher is present.

## Modified files relative to the last delivered ZIP

- `Content.py`
- `ContentSources.md`
- `CreationInstructions.md`
- `HowToAddImages.md`
- `QuestionManager.md`
- `ReadMe.md`
- `UpdateGuide.md`
- `Verification.md`
- `build_question_images.py`
- `main.py`
- `question_content.py`
- `questions.json`
- `static/app.js`
- `static/images/sample23.png`
- `static/index.html`
- `static/presenter.html`
- `static/style.css`
- `tests/test_game.py`
- `tests/test_question_manager.py`

## Added or removed files

None.

## Validation

- 28 Python API/manager tests pass, including reveal-source secrecy, save preservation and unsafe-link rejection.
- Full ten-round presenter/player DOM checks and local-manager save/upload checks pass. All four RFC credits are verified on both roles at reveal, absent during voting and preserved during polling.
- Image-zoom, presenter Enter/Next and post-bonus workflow checks pass. JavaScript syntax checks pass.
- The exact SQL runs against a fabricated SQLite fixture with correct filtering, grouping, salary averages and ordering. The SQL PNG was visually inspected for legibility/clipping.
- The archive is freshly extracted, checked against tested source and validated for matching decks and decodable images. Physical phone/projector rendering and live Supabase/Vercel/PostgreSQL deployment were not tested.
