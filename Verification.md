# Verification — October 5, 2026

## Pixelation update

Both Trump cards have been visually inspected at full resolution: profile pictures, names and handles use coarse pixelation and no longer show readable author text. Pixel comparison against the previous cards confirms all changes stay within the three identity rectangles; the post writing and interface outside them remain identical. LinkedIn and Teams PNGs remain byte-identical. Fresh extraction confirms all ten questions and media are present and JSON matches the Python fallback. The 25 Python tests still pass.

## Checks completed

- **25 Python API tests pass**: complete ten-round scores/streaks, authentication, vote guards, QR generation, timer boundaries, manager uploads/saves, room snapshots, JSON/fallback equivalence and bundled media.
- A presenter-selected **10 seconds** applies to every round, despite conflicting legacy question timers. Votes are accepted at 9.99 seconds and rejected at the deadline.
- API-to-DOM checks play all ten actual bundled questions. The presenter starts in the QR-only lobby, then gets centered questions without a live leaderboard. Questions contain only the content; reveals contain only AI or HUMAN.
- Final-placement checks cover medals 1/2/3, numeric ranks 4/4/6, exact scores/names and tied gold medals. The presenter final screen has **no bonus question, link or further action**. Phones automatically get the bonus question below their placements. A choice reveals AI without changing scores; the reveal persists when updated rankings cause a rerender. The legacy standalone `/bonus` route remains available but is not linked from the presenter.
- Real presenter form checks verify the timer, QR failure/retry, copy link and Start controls. No first question is shown before Start.
- The actual local manager loads all ten questions without missing-media warnings, previews Teams and both Trump posts, and saves custom uploaded/online audio and video. The default deck has **eight images and two texts**, five AI and five HUMAN, no audio/video rounds or remote question media.
- The LinkedIn writing and AI firewall post match the previous version exactly. All four social PNGs were rebuilt and inspected for text bounds. The Teams reply uses understandable but off-topic automation claims. The cat image is absent from the deck and package.
- The genuine post's unchanged 15-word text and May 16, 2025 date were checked against the American Presidency Project archive, linked in ContentSources.md. Current Teams layout reference: Microsoft's combined Chat screenshot, accessed October 4, 2026.
- Python compiles and public JavaScript passes syntax checks. The complete ZIP is freshly extracted, compared byte for byte with the project, checked for ten matching JSON/fallback rounds and decodable media, and tested again from that extracted folder. Runtime installations, private `.env`, caches and authoring research are excluded.

## Limits

JSDOM checks verify DOM behavior and selected computed styles, not actual browser/projector rendering. The social PNGs are UI reconstructions, with drawn anonymized avatars; they are not captures of real LinkedIn or Teams accounts. The real Trump post preserves original words; the firewall parody is fictional. All current media plays locally without external media hosts.

No live Supabase/Vercel account deployment or database migration was performed. Rehearse on the event browser and intended audience size. Production capacity at the 200-player limit has not been load-tested. This is a known-origin game, not an authorship detector.
