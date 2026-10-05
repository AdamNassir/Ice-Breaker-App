# Verification — October 5, 2026

## Current update checks

- **25 Python API tests pass.** Full ten-round scoring/streaks, authentication, QR codes, timer boundaries, manager uploads/saves, room snapshots and JSON/fallback/media equivalence still pass. Invalid circle coordinates (out of bounds, zero radius and missing coordinates) are rejected without writing a deck.
- A presenter-selected 10 seconds applies to every round despite conflicting legacy question timers. Votes are accepted at 9.99 seconds and rejected at the deadline.
- Caption and circle fields are withheld from live question payloads. The reveal API returns the exact configured fields after the deadline.
- API-to-DOM checks run all ten actual questions for presenter and player. Real-photo reveals show their exact subject/date/source captions and correct source links. Social posts and text questions show only AI or HUMAN. The painting's SVG circle is absent during voting, appears at reveal, and uses the expected natural-image dimensions and coordinates. Its position was visually checked with a native SVG preview.
- Text paragraphs preserve the complete original wording and line breaks in the DOM while using tighter spacing and smaller presenter type. Text cards fit their content instead of reserving an empty minimum-height area. LinkedIn, both Teams messages, both Trump posts and both textual questions are unchanged in wording. The LinkedIn PNG and original painting remain byte-identical.
- The rebuilt Teams image has larger messages and the closed PDF attachment; the document panel is absent. The compact white Truth Social and dark X cards follow the user-supplied reference layouts. Both retain coarse pixelation over avatar, name and handle. All three updated PNGs were visually inspected for text bounds.
- Confetti originates from every occupied podium place, occurs once per room, survives ordinary polling without restarting, and is skipped for reduced-motion preferences. Rank updates do not trigger another burst. Final-placement checks cover medals 1/2/3, numeric ranks 4/4/6, exact names/scores and tied gold medals.
- The presenter stays on final placements with no bonus link or question. Phones automatically get the unscored bonus below placements. Choosing an answer reveals AI without changing scores; the reveal survives polling/rerenders.
- The actual local manager loads all ten questions, preserves captions and circle coordinates when saving, previews the social PNGs, and supports custom uploaded/online audio and video. The default deck remains eight images and two texts, five AI and five HUMAN, with no audio/video or remote question media.
- Presenter form checks verify the QR-only lobby, timer selection, QR failure/retry, Copy player link and Start controls. No first question or live presenter leaderboard appears before Start.
- Python compiles and JavaScript syntax checks pass. The complete ZIP is freshly extracted and compared byte for byte, then checked for matching ten-round JSON/fallback content and decodable media. Private `.env`, runtime installations, caches and authoring research are excluded.

## Limits

JSDOM checks establish DOM behavior and selected computed styles, not actual browser/projector rendering. The rebuilt PNGs and circle preview were visually inspected; rehearse the game in the event browser. All current media is bundled locally. No live Supabase/Vercel deployment or database migration was performed; capacity at 200 players has not been load-tested.

Social screenshots are UI reconstructions with anonymized drawn avatars. The genuine Trump writing is preserved from its verified source; the firewall post and Teams/LinkedIn texts are fictional. This is a known-origin quiz, not an authorship detector.
