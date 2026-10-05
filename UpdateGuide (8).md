# Completed update — full French news website pages

## Resulting behavior

- Both default article questions are now entirely in French. App controls, neutral titles and short introductions remain English. The other eight questions/media remain unchanged. Both deck files are equivalent; ten rounds, eight images/two texts and seven AI/three HUMAN.
- Le Parisien replaces the New York Post reference. The presentation is a full native page: actual vector logo, French navigation/local strip, headline/chapo/byline, main article, sidebar, related stories and footer. The old screenshot-based masthead asset is removed. All story text remains editable through the existing News article manager option.
- The complete embedded page scrolls on phones/presenter and adapts to its container width. Polling and answer reveal preserve the reader’s place; the next article starts at the top. The game timer, voting, QR lobby, Next/Enter, image zoom, podium/confetti and phone-only bonus/workflow retain their behavior.
- The two incidents are AI-written French fiction. Layout references do not establish publication by Le Parisien. Original French sidebar/related filler, decorative CSS thumbnails and a generic byline complete the page without borrowing unrelated reporting. Private provenance remains outside live payloads.

## Exact-copy requirement — remaining limitation

The page is a full website reconstruction rather than an article screenshot. The logo bytes are authentic and unchanged. LayoutSources.md records the official article and the designer’s dated 2018–2019 whole-page reference. The publisher’s live HTML/CSS and licensed fonts are not copied; native browser pixel comparison was unavailable. The request for proven pixel identity remains open for viewport-matched browser comparison. Do not describe this reconstruction, or the unchanged LinkedIn/X/Teams cards, as pixel-identical.

## Install / redeploy

1. Extract this complete ZIP and replace the app source, preserving your own .env, secrets and virtual environment. Replace questions.json and Content.py together to adopt the French articles.
2. Include static/newsarticle.js, static/newsarticle.css and static/branding/publication.svg, plus the updated static/app.js and player/presenter HTML. Remove the obsolete static/branding/news-layout-reference.png.
3. Restart the local manager and refresh it. News article preview now shows the entire French publication page. First paragraph = headline, next = chapo, remaining blank-line-separated paragraphs = body.
4. Redeploy through your usual Vercel workflow, then create a **new room**. Existing room snapshots keep their old story text. No new production dependency or Supabase migration is needed. Frontend cache keys are refreshed.
5. Rehearse full-page scrolling, French wrapping, selected timing and voting on the event phones/projector; verify exact layout matching at the same viewport if required.

## Validation

42 Python tests and the complete check_project.py gate pass, including all JavaScript syntax and API-backed frontend checks. New checks exercise the complete game/manager page, French language metadata/navigation, exact headline/chapo/body preservation, trusted logo rendering alongside hostile-text escaping, CSS grid/scrolling, polling/reveal scroll preservation and new-article reset. Existing upload/save, source secrecy, timing, Next/Enter, image gestures/highlights, placements/confetti and bonus/workflow checks pass. The primary full-page design reference and logo were inspected. The full archive manifest and bytes are verified, and the complete gate is run again on a fresh extraction before delivery. No physical phone/projector, live Vercel/Supabase or pixel screenshot comparison is claimed.

## Modified files relative to the previous complete ZIP

- `Content.py`
- `ContentSources.md`
- `CreationInstructions.md`
- `HowToAddImages.md`
- `LayoutSources.md`
- `QuestionManager.md`
- `ReadMe.md`
- `UpdateGuide.md`
- `Verification.md`
- `manager_assets/index.html`
- `questions.json`
- `static/app.js`
- `static/index.html`
- `static/newsarticle.css`
- `static/newsarticle.js`
- `static/presenter.html`
- `tests/frontend/game.cjs`
- `tests/run_frontend.py`

## Added files

- `static/branding/publication.svg`

## Removed files

- `static/branding/news-layout-reference.png`
