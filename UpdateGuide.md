# Completed update - repository formalization and post-reveal workflow

## Resulting behaviour

- Added CreationInstructions.md as one complete upfront specification in the attached creation brief's style, with code fragments, setup steps and clear restrictions. Individual question wording, media and sources remain in their separate deck files.
- Added AGENTS.md so future agents read the creation brief and saved update request, implement/test/fix iteratively, then replace completed requests with a reviewable report. Human review and testing remain part of the loop.
- After a player answers the unscored "Was this game made with AI or not ?" question, AI is revealed and the ordered development sequence appears. It covers the instruction file, agent creation/self-testing loop, human code review/testing, question-manager authoring with instructions/sources, saved UpdateGuide.md requests and report replacement, and another human test/update cycle.
- The sequence is labeled an illustrative reconstruction. Saving a file is a handoff to a running agent workflow, not a deployed app feature or automatic file watcher.
- The phone reveal/workflow persists through polling, results rerenders and a restored answered session. The standalone /bonus page has the same explanation. The presenter stays on final placements without a bonus/workflow.
- Removed the abandoned document/signature authoring tool. The accepted ten-question deck, images, manager and game timing/scoring remain unchanged.

## Install

1. Extract the complete ZIP. Add the three new files, replace the modified files and remove the five abandoned tool files listed below. Preserve your .env and custom deck/media.
2. For deployment, commit the frontend changes and new workflow.js asset, then redeploy to Vercel. No new dependency or Supabase migration is required.
3. Hard-refresh player/presenter pages to load the versioned scripts/styles. Create/join a room and play through final results; either bonus answer should reveal AI and the six-step explanation only on the player screen.
4. Review CreationInstructions.md and AGENTS.md in the repository. For the next change, replace this report with a pending request and acceptance checks, save it and have the running agent read it. The agent replaces completed requests with a report after implementation and validation; unfinished requests must remain visible.

## Modified files relative to the last delivered ZIP

- `.gitignore`
- `ReadMe.md`
- `UpdateGuide.md`
- `Verification.md`
- `static/app.js`
- `static/bonus.html`
- `static/bonus.js`
- `static/index.html`
- `static/presenter.html`
- `static/style.css`
- `tests/test_game.py`

## Added files

- `AGENTS.md`
- `CreationInstructions.md`
- `static/workflow.js`

## Removed files - abandoned document tool

- `DocumentStampTool.md`
- `document_stamp_tool.py`
- `document_templates/example.json`
- `requirements-document-tool.txt`
- `tests/test_document_stamp_tool.py`

If you stayed on the earlier code/GraphRAG release and never installed the document tool, these removal steps do not apply. No supplied question/media files are changed.

## Validation

- 27 Python API/manager tests pass, including public workflow delivery and private-document route checks.
- Full ten-round API-to-DOM game, final rankings, local manager and bonus/workflow checks pass.
- Dedicated post-reveal checks pass for both standalone answers, a player AI answer, restored answered state, hidden-before-answer workflow, exact step order, unchanged scores/no vote API and stable polling.
- Image-zoom gestures and presenter Enter/Next checks pass; JavaScript syntax checks pass.
- The complete archive is freshly extracted and compared with the tested source. Actual phone/projector rendering and live Supabase/Vercel deployment were not tested in this update.
