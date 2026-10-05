# Completed update — logo blending, visible news layout, nine rounds and expanded SQL

## Resulting behavior

- The complete LogicLever JPEG remains unchanged. CSS multiply blending in the game and manager blends its white background into the surrounding surface, retaining its tagline and contain sizing. TotalEnergies is unchanged.
- The painting intro is now only “AI or HUMAN?”. Its neutral alt text does not point out a hidden character. The server also removes the exact old hint from public views of existing snapshots, without changing saved room data.
- The active deck now contains **nine rounds**: seven images/two French text articles, seven AI/two HUMAN. The previous tenth moth-logbook round is removed. Its image remains available for custom/older decks. Rankings and the phone-only bonus follow round nine. A perfect game now earns 1,550 points.
- The employee-data SQL card is expanded with readable comments, two CTEs, four source tables, joins and a conditional-aggregate pivot. Pre-aggregation prevents duplicated totals. The HR use case remains implied in the code; the short introduction does not narrate it. AI classification is unchanged.
- The full Le Parisien page renderer is preserved. A reproduced legacy failure path caused older bundled articles to fall back to plain text because their stored format flag was missing/defaulted to plain. The shared parser and public-state projection now recognize those two specific legacy title/headline pairs, including existing room snapshots. Current article titles missing the format field receive news style; custom/ordinary explicit plain text stays supported. Stored room content is not rewritten. The complete frontend page uses masthead, French navigation, article/chapo/byline, sidebar, related stories and footer.
- HTML responses use no-store, and game/manager cache keys are refreshed. New checks load the actual shipped HTML, scripts and styles over HTTP to detect missing asset integration, rather than relying solely on manual script/CSS injection.

## Install / redeploy

1. Extract this **complete ZIP** and replace all delivered app source, keeping your own .env, secrets and virtual environment. Deploy main.py and question_content.py together. Use the included questions.json and Content.py together to adopt the nine-round default.
2. Include all static files, especially the expanded static/images/sample23.png, static/style.css, static/newsarticle.js, static/newsarticle.css and static/branding/publication.svg. The shared renderer must be present along with its CSS. No production dependency or Supabase migration is added.
3. Restart the local question manager and refresh it. If you preserve a custom deck, select Text presentation → News article for your article entries and save. The specific legacy bundled entries are recognized automatically; arbitrary plain text is not forcibly reclassified.
4. Redeploy through the usual Vercel workflow and open /presenter from the new deployment. Create a **new room** to adopt nine rounds/new content. Existing snapshots keep their original question count/text, while the known news-layout and exact painting-hint display fixes apply to them.
5. Verify the nine-round flow, full news-page scrolling and SQL zoom on the event phones/projector. No automatic publishing or deployment was performed.

## Validation

43 Python tests and the complete check_project.py gate pass. Tests cover nine-round scores/final advancement, legacy article deck/API migration without snapshot mutation or source leaks, preservation of custom plain text, old painting-hint removal and no-store HTML headers. New HTTP-loaded player/presenter/manager checks fetch and execute the actual shipped page resources and verify computed article grid/masthead/scroll styling, navigation/sidebar/footer and logo blending. Existing save/upload, full news/plain preview, timer, Next/Enter, image gestures, circle, podium/confetti and bonus/workflow checks pass. The expanded SQL screenshot was visually inspected. Its relational behavior was exercised on synthetic SQLite data with only DATE-literal syntax adapted; this is not PostgreSQL execution. The archive manifest/bytes and a fresh extraction are verified with the full gate before delivery.

## Remaining exact-copy limitation

Le Parisien is a complete native page reconstruction, with the authentic vector logo and references recorded in LayoutSources.md. Neither its full layout nor the unchanged LinkedIn/X/Teams cards is proven pixel-identical. Native Chromium still could not launch here, so no physical browser/phone/projector screenshot comparison, live Vercel/Supabase test or exact licensed-font match is claimed. Preserve the viewport-matched comparison requirement for human review.

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
- `manager_assets/index.html`
- `manager_assets/style.css`
- `question_content.py`
- `questions.json`
- `static/bonus.html`
- `static/images/sample23.png`
- `static/index.html`
- `static/presenter.html`
- `static/style.css`
- `tests/frontend/game.cjs`
- `tests/frontend/keyboard.cjs`
- `tests/run_frontend.py`
- `tests/test_game.py`

## Added files

- `tests/frontend/resources.cjs`

## Removed files

None. The tenth question is removed from the deck; its media remains available for older rooms/custom decks.
