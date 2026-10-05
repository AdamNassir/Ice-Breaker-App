# Install the presentation and reveal update

This complete ZIP keeps ten English rounds, five AI and five HUMAN, with all local media and the matching JSON/Python decks.

## Changes

- Teams messages are larger and use the full chat area. The PDF stays as an attachment; its interior panel is removed.
- Text questions have smaller presenter type and compact paragraph spacing; no words or excerpts are removed.
- Truth Social follows the supplied compact white reference; X follows the supplied dark reference. Post wording and coarse identity pixelation remain.
- The final podium emits a short confetti burst once per room. Reduced-motion preferences skip the animation. The presenter stays on rankings; the bonus remains phone-only.
- Real-photo reveals show what the image depicts, its date and source link. Social posts receive no context.
- The painting gets a red circle around Inspector Gadget only at reveal. The original image is unchanged; the circle is a responsive SVG overlay.

## Install

1. Back up custom questions and stop local servers.
2. Extract the enclosed project and replace **all modified files** listed below. In particular, replace `main.py` and `question_content.py` together with `questions.json` and `Content.py`: the new reveal fields need the updated parser/API.
3. Preserve your `.env` and deployment environment variables. No dependency installation or Supabase migration is needed.
4. Restart the manager and choose Reload saved; confirm ten questions and no missing-media error.
5. Commit all modified files, including the three PNGs, redeploy to Vercel and hard-refresh presenter/player pages.
6. Create a **new room** to load the new captions and circle. Existing rooms keep their older question snapshots.

## Modified files relative to the previous ZIP

- `Content.py`
- `ContentSources.md`
- `HowToAddImages.md`
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
- `static/images/sample19.png`
- `static/images/sample21.png`
- `static/images/sample22.png`
- `static/imagestyle.css`
- `static/index.html`
- `static/presenter.html`
- `static/style.css`
- `tests/test_game.py`
- `tests/test_question_manager.py`

No files were added or removed in this update.

## Check before presenting

Choose ten seconds, join on a phone, then Start. Check the enlarged Teams conversation and compact texts. At the three real-photo reveals, check subject/date/source; check no extra text appears after social posts. The red circle must stay hidden while voting and appear on the painting's reveal. At final results, check confetti and placements, with the bonus question only on phones.

The photo caption can be edited in the manager's Answer notes section. Circle coordinates, text spacing and confetti settings are documented in HowToAddImages.md.
