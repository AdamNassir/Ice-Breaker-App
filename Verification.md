# Verification — October 4, 2026

## English fun-deck update: passed

- **23 Python API tests** pass: the complete ten-round game, streaks and 1,750-point perfect score; auth/vote/timer guards; QR access; deck diagnostics; editor save/backup/revision behavior; media uploads; URL/YouTube validation; clip bounds; new-room snapshots; and bundled JSON/fallback equivalence.
- Actual bundled `questions.json` creates a room, serves all local assets and completes all ten rounds. Live question state withholds answer, explanation, credits and source links. Root question/answer files and the manager API are not served by the public game.
- Actual manager HTML/JavaScript exercised against a running isolated local manager in JSDOM: loads all ten questions without missing-media warnings; previews local Hopper audio, online Alloy audio and YouTube video; edits/saves clip times and links; switches to a local MP3 upload; clears the previous link; preserves upload bytes and saves again.
- Presenter and player JSDOM checks use snapshots from a full API playthrough of the bundled JSON. All ten rounds render the correct text, four images, two audio players and two video players; answers appear only at reveal. Repeated polling preserves the same media element while a round remains live, so playback is not restarted. English source explanations and final results render without JavaScript runtime errors.
- Shared player checks confirm YouTube IDs are validated, deceptive/credentialed YouTube URLs are rejected, privacy-host embeds use English parameters and clip boundaries, and the iframe supplies an origin referrer. Native media seeks to start and pauses at end in the DOM event checks.
- Both JavaScript application scripts and the new shared player pass syntax checks. Python sources compile.
- Four new JPEG files fully decode. The Hopper MP3 decodes and contains an authentic English excerpt of about 8.65 seconds (8.70 seconds including encoder padding). The synthetic voice and generated-video source URLs returned media during preparation; the linked clips were inspected. Generated images were visually inspected before inclusion.
- The download archive is rebuilt with both default deck files, all required local media, shared playback code, sources/credits and installation instructions. Temporary recordings, QA tools, dependencies and databases are excluded.

## Limits of these checks

- JSDOM establishes elements, paths, state and controls; it does not establish actual audio/video decoding on mobile Safari, rendered layout, YouTube embedding permission, advertisements or live internet reliability. Rehearse in the event browser on the event network.
- Three rounds remain online links: Alloy audio, Boston Dynamics YouTube and Runway video. Host URLs, embeds, codecs and availability can change. YouTube branding and the retained Runway watermark can provide clues. No external video/music copies are bundled.
- No live Supabase/Vercel account was available for deployment checks. No database migration or runtime dependency changes are part of this update.
- The deck is designed for visual surprise and discussion, not a validated AI detector or measured difficulty progression. Labels are based on documented generation/recording origin. Human camera tricks still count as HUMAN.
- Production load and the maximum 200-player limit have not been capacity-tested.

## Before the event

Follow UpdateGuide.md, deploy all changed code, questions.json and its local assets, then create a new room. Play both voice clips and both videos from the actual laptop/speakers and two phones. Confirm the QR link is public, voting closes on time, streak scores update and final standings appear. Replace any blocked clip with a recording you have permission to host before participants join.
