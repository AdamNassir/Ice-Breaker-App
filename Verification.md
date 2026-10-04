# Verification — October 4, 2026

## Tweet replacement update

- **25 Python API tests pass**, covering the full ten-round game, streak scores, auth/vote guards, QR generation, timer boundaries, question-manager uploads and saves, deck snapshots, bundled JSON/fallback equivalence, and the unscored bonus route.
- The timer test sets the room to 10 seconds while legacy questions contain conflicting 25/120-second values. Every round uses exactly 10 seconds; votes are accepted at 9.99 seconds and rejected at the deadline.
- The real presenter form is exercised in JSDOM: submitting 10 seconds creates a QR-only lobby with no first question or ranking; QR failure stays visible, retry restores the code, Copy player link works, and clicking Start sends the correct control action, hides the QR and displays the first question with a 10-second timer.
- Presenter/player DOM checks use an API playthrough of all ten bundled questions. Content-only questions and AI/HUMAN-only reveals render correctly. The presenter has one content column and no live leaderboard. The QR lobby is hidden during rounds and final results. Repeated polling preserves media elements rather than restarting playback.
- Final-placement checks cover six API-ranked entrants, medals for 1/2/3, numeric ranks 4/4/6, exact names/scores, and tied gold medals. The bonus link opens `/bonus`; either choice reveals AI without a room or scoring request.
- The local manager opens the actual ten-question JSON without missing-media warnings, previews the Teams image and both new tweet cards, and saves additional custom video/audio questions. Switching an online video to an uploaded MP3 preserves upload bytes and clears the former link. Audio/video capability remains for custom decks despite removing all default recording questions.
- Python sources compile; public JavaScript passes syntax checks. The new tweet cards were visually inspected for text bounds and blurred identity fields; the earlier LinkedIn/Teams screenshot assets remain unchanged. The historical moth JPEG decodes. Both deck files contain the same ten questions and answer balance (five AI, five HUMAN).
- The bundled deck contains exactly nine image questions and one text question, no audio/video rounds and no remote question media. The genuine tweet wording/date were verified against X's public oEmbed response; the second replacement is original AI-written parody.
- The final ZIP is built from the current project, extracted into a fresh folder, compared byte for byte, and tested for complete deck/media loading. Runtime dependencies, databases, private `.env`, caches and authoring research files are excluded.

## Limits

DOM/computed-style checks do not establish actual projector layout. Rehearse in the event browser. All current question media is bundled; no external media playback is required. No live Supabase/Vercel deployment was available for account-level checks, and no deployment or database migration was performed.

This is a known-origin game, not an authorship detector or a measured difficulty benchmark. For the social screenshots, judge the post or reply text. The genuine tweet reproduces original words in a reconstructed interface; its displayed avatar is a blurred placeholder. Other social posts/conversations are fictional. The AI parody is not a real statement by Trump. Production capacity at the 200-player limit has not been load-tested.
