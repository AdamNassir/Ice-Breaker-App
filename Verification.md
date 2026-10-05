# Verification — October 5, 2026

## Branding and question update

- Extracted both original PNG logos from the supplied DOCX. SHA-256 byte comparisons confirm that delivered logos equal the embedded source PNGs. Original dimensions are preserved; the app scales them with contain framing rather than redrawing/recoloring. All player/presenter/bonus entry routes and the manager reference both local assets.
- Updated both game/manager palettes to blue/red and refreshed relevant CSS/JS cache keys. Frontend DOM checks assert the blue/red design tokens and both logo identities. Metallic final podium accents remain localized to medals/placements.
- The managed JSON deck and Python fallback validate identically: ten rounds, eight images/two texts, seven AI/three HUMAN. Both textual questions are new AI-written plausible fictional news articles. All titles/short introductions are English; the Macron post and Teams messages are French.
- Replaced the active motorcycle-football photograph with a real Michael Jordan dunk. Source JPEG bytes and SHA-1 match the high-quality Commons record. Its reveal carries the photographer, subject, season and source. No new generative edits are made to human photographs.
- Rebuilt and visually inspected the French Macron parody and French Teams screenshot. Macron’s name, handle and licensed real portrait are readable with no blur/pixelation. The invented post is documented as AI fiction. Teams keeps anonymized identities, attachment-only layout and a simpler document-search request; the manager’s mismatched reply is explicitly identified as the classification target.
- Added a neutral title and short introduction above each live/revealed question on presenter and phones. Actual API-generated DOM checks cover all ten rounds, exact title/intro text, hidden lobby content, answer/source privacy, revealed credits, rankings and phone-only bonus behavior.
- **42 Python tests pass**: game/API, local manager and 13 watcher/process tests. The full `python check_project.py` gate passes, including JavaScript syntax and actual API-backed DOM game/manager, zoom, keyboard and workflow checks. The new test verifies local logo routes/content and their inclusion in all public entry views.
- Regression checks verify that the presenter-selected ten-second timer applies to every round, votes close at the server deadline, scoring remains atomic, Next/Enter immediately starts subsequent rounds, phone image gestures retain position at reveal, the Gadget circle stays aligned, final placements/confetti stay minimal and the phone-only bonus never changes scores.
- Complete ZIP manifest and byte comparisons are verified against tested source; a fresh extraction runs the same complete gate with existing development dependencies. Dependencies, runtime databases, credentials, caches, watcher checkpoints/logs and QA artifacts are excluded. Original LinkedIn, SQL, painting and other unaffected media remain byte-identical to the previous release.

## Limits

These are local API, process and JSDOM checks. JSDOM verifies selected DOM/style behavior, not physical phone/projector rendering. No live Supabase/Vercel deployment, PostgreSQL execution or capacity test was performed; deploy manually, create a new room and rehearse on the devices used for the event.

The local agent implementation is retained. Watcher tests use real subprocesses with a deterministic fake CLI on Linux. Previously inspected Codex CLI flags/help do not constitute an authenticated model run. The author still needs CLI login, doctor and a small real request on their machine; native Windows sandbox/launcher/process cancellation and actual account integration were not exercised here. The post-bonus sequence remains illustrative, not a literal history.
