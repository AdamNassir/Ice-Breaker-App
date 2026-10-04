# Install the tweet replacements

This complete ZIP removes the two voice questions from the starter deck and replaces them with anonymized tweet-style images. There are still ten scored rounds: nine images and one text, five AI and five HUMAN. No audio/video round or remote question-media link remains in the default deck.

## Install

1. Stop the local game and manager; back up your folder and custom questions.
2. Extract the ZIP. `main.py`, `Content.py` and `questions.json` must be together in the enclosed `Ice_Breaker_Game_App` project root.
3. Replace the modified files and add the new PNGs listed below. Replace **both `questions.json` and `Content.py`** to install the new questions; JSON takes priority over the fallback.
4. Keep your `.env`, database and deployment environment variables. No package installation or Supabase migration is required.
5. Restart locally and click **Reload saved** in the manager. Check ten questions, with images in positions 3 and 7 and no missing-media warnings.
6. Commit the changed files and both new PNGs, redeploy, refresh presenter/player pages, and create a **new room**. Existing rooms retain their previous questions.

## New questions

Round 3 reproduces the wording of a verified Donald Trump tweet, displayed in a reconstructed interface with blurred profile picture, name and handle. Round 7 is an original AI-written parody in a similar exaggerated style, about building a huge firewall. The cards use the same layout and omit date and engagement counts. The genuine source and parody origin are recorded privately in `ContentSources.md` and the manager. Before opening the room, explain that social-post rounds classify the writing.

The existing longer April Fools text remains one question. No new April Fools questions were added. The QR-first lobby, centered presenter questions, final-only presenter rankings, podium and unscored bonus question remain available.

## Modified files relative to the previous ZIP

- `Content.py`
- `questions.json`
- `build_question_images.py`
- `static/index.html`
- `static/presenter.html`
- `static/audio/README.md`
- `tests/test_game.py`
- `ReadMe.md`
- `HowToAddImages.md`
- `ContentSources.md`
- `Verification.md`
- `UpdateGuide.md`

## New files

- `static/images/sample21.png` — anonymized genuine post.
- `static/images/sample22.png` — anonymized original AI parody.

All other game code, requirements, SQL and deployment configuration are unchanged. Legacy audio is retained for older room snapshots and custom decks; it is not a question in the new starter deck. The local manager still supports custom audio/video uploads.

## Check before presenting

Create a fresh room, scan the QR on a phone, start the first round and check that the QR disappears. Confirm rounds 3 and 7 show the new images. Choose ten seconds and verify the timer, then complete the game and open the bonus question. The default questions require no access to external media hosts.
