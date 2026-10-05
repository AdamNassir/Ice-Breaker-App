# Completed update — three HUMAN rounds

## Resulting behavior

- Nine rounds now contain six AI answers and three HUMAN answers.
- Round 1 replaces the generated French LinkedIn text with the verbatim 21-word opening of Augustin de Magnitot's publicly attributed AB Tasty / VivaTech 2019 post. The source URL is recorded in the private deck/source notes. It is marked HUMAN as requested, on the basis of historical human attribution; the author's private writing process has not been independently verified.
- The anonymous LinkedIn layout is retained. Hashtags are blue inline, the observed reaction count is 21, and invented recent timing/comment counts were removed. No explanatory commentary is added to this social-post reveal.
- Round 4 replaces Tesla with the existing motorcycle-football photograph from Germany, August 1931. It is HUMAN, and the reveal gives its subject, date and Bundesarchiv / CC BY-SA 3.0 Germany credit. The original bundled sample15.jpg bytes are unchanged. Tesla's old asset remains available for custom decks and existing rooms.
- The other seven question records and all unrelated static assets remain unchanged. JSON and Content.py fallback match. QR lobby, authoritative timer, immediate Next/Enter, phone zoom, final rankings/confetti and bonus behavior remain intact.

## Install / redeploy

1. Extract the complete ZIP, replacing delivered source while preserving your own .env, virtual environment and secrets.
2. Redeploy manually and create a NEW room to load the revised deck. Restart/reload the local question manager.
3. No new dependency. The editable LINKEDIN_POST and linkedin() renderer are in build_question_images.py; retain source wording/provenance when rebuilding sourced excerpts.

## Validation

43 Python tests and the complete check_project.py frontend/syntax gate pass. The revised LinkedIn image and existing motorcycle-football photograph were visually inspected. JSON/fallback equivalence, unchanged other seven rounds, unchanged unrelated assets, archive manifest/CRC/bytes and exact changed paths were verified against the preceding ZIP. A fresh extraction passes the same complete gate.

## Limits

The LinkedIn visual is a reconstructed anonymous layout containing a real excerpt, not an unmodified screenshot of the original author. The HUMAN label reflects the requested historical attribution, not proof that no writing tools were used. Physical phone/projector and live Vercel/Supabase testing remain unverified as documented in Verification.md.

## Modified files since the previous complete ZIP

- `Content.py`
- `ContentSources.md`
- `HowToAddImages.md`
- `LayoutSources.md`
- `ReadMe.md`
- `UpdateGuide.md`
- `Verification.md`
- `build_question_images.py`
- `questions.json`
- `static/images/sample18.png`
- `tests/test_game.py`

## Added / removed files

None.
