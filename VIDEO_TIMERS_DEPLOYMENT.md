# IceBreaker — video playback and per-question timers (5 Nov 2026)

## What changed
- Each question can choose **Use presenter's room timer** or **Custom timer** (5–120 seconds). The selection is persisted in the question deck as `timer_mode: "global"` or `timer_mode: "local"`, with `seconds` for a local timer.
- For older decks, `seconds` without an explicit `timer_mode: "local"` continues to follow the presenter timer. This is intentional: the old editor saved legacy values that it did not honor.
- In an IceBreaker video round, the app attempts playback when the round starts. The presenter's video completion event starts the authoritative voting countdown. The countdown does **not** run during the video. A new video player is not inserted again when voting opens.
- Video controls are hidden in the game (not in the editing preview). YouTube embeds use `controls=0` and supported reduced-overlay flags. A separate `Play / resume video` button appears when autoplay is blocked. Browser autoplay policies and YouTube branding are not under the app's full control.
- The video completion transition is presenter-controlled. If the video cannot finish, the presenter can press the existing explicit fallback to open voting.

## How to use
1. Deploy the updated **IceBreaker** project to the existing Vercel application. Preserve `DATABASE_URL`, `PRESENTER_PASSWORD` and `BLOB_READ_WRITE_TOKEN` environment variables and the existing Supabase table. Do **not** delete/recreate the database.
2. In `https://YOUR-ICEBREAKER.vercel.app/deck-manager`, open a question, then choose **Voting timer for this question**:
   - **Use presenter's room timer** = inherit presenter setting for that room.
   - **Custom timer for this question** = enter whole seconds from 5 to 120.
3. Save the deck. New rooms use the updated settings. Existing rooms preserve their snapshot.
4. For a video question, set the `media_url` (YouTube or direct video), optionally `media_start`/`media_end`; the countdown starts after the presenter video ends.
5. Test autoplay on the actual **presenter device and browser**. On mobile browsers with audio, autoplay may require a tap on **Play / resume video**.

## Notes
- YouTube's own logos or overlays may still appear. YouTube does not provide a supported way to suppress *all* branding; to get a fully custom chrome-free player, use a properly licensed MP4 or WebM source instead.
- IceBreaker live-game UI polls the server and all players receive the same server authoritative voting deadline; network or device backgrounding may delay when video appears on a participant device.
- Tests run offline: Python backend suite and a deterministic JS media flow; live YouTube playback and Vercel Blob access were **not** tested.
- This ZIP excludes private credentials and runtime databases.
