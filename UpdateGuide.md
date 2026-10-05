# Completed update — French LinkedIn post in the new supplied layout

## Resulting behavior

- Round 1 is an original French tech-management LinkedIn post, replacing the English roadmap-deletion satire. It describes a plausible but invented rollout using an agent for tickets/documentation/tests and a fictional delivery anecdote. The requested rhetorical devices appear: repeated Ce n’est pas… C’est…, Moins… Plus…, parallel lists and a three-adjective phrase, followed by an audience question and hashtags.
- The writing was grounded in three public French LinkedIn tech/AI posts. Exact reference links and the original-fiction provenance are in ContentSources.md. No source post is quoted/copied, attributed to the fictional account or treated as proof of its author using AI.
- The updated PNG follows the attached image(4).png geometry, reconstructed natively at 3×: compact name/avatar/Follow header, body margins and regular type/line spacing, blue hashtags and reaction/comment summary. Removed the old extra action-button row. Source layout reference bytes are preserved unchanged in layout_sources/linkedin-reference.png, replacing the earlier reference. The name/avatar/headline remain fictional and blurred as requested.
- LINKEDIN_POST is an easily editable multiline French constant; linkedin() controls its measured layout. The final blank-line-separated paragraph is rendered as blue hashtags. The question title/classification target remain neutral English; answer is AI with no extra public explanation.
- The eight other question records and all unrelated static assets are identical to the preceding ZIP. Nine rounds, timing, QR, Next/Enter, zoom, rankings/confetti, articles, Teams and bonus remain intact. JSON and Content.py fallback are equivalent.

## Install / redeploy

1. Extract the complete ZIP, replacing delivered app source while preserving your own .env, virtual environment and secrets.
2. Include static/images/sample18.png, questions.json and Content.py together; redeploy manually and create a NEW room for consistent updated metadata/source notes. Restart/reload the local manager.
3. No new runtime dependency. Optional image authoring uses Pillow as already documented. Edit LINKEDIN_POST and run build_question_images.py to rebuild later; HowToAddImages.md explains the final hashtag paragraph and reference crop.

## Validation

43 Python tests and the full check_project.py gate pass, including actual API states and game/manager asset loading, nine-round advancement/scoring, authoritative ten-second timing, Next/Enter, phone zoom/reveal preservation, final placements/confetti and bonus/workflow. The new 1365 × 1536 PNG was visually compared with the supplied 455 × 540 reference. Reference bytes are identical to the attachment; JSON/fallback match. A byte comparison confirms unchanged other rounds/static assets. Complete archive manifest/bytes and changed paths are verified against the previous ZIP; a fresh extraction passes the same complete gate.

## Limits

The supplied geometry is reconstructed with available fonts and new text/blurred fictional identities; no licensed-font or changed-text pixel identity is claimed. Native browser/physical phone/projector and live Vercel/Supabase testing remain unverified as documented. Rhetorical patterns were deliberately authored for this round; they are not a reliable detector of real-world AI writing.

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
- `layout_sources/linkedin-reference.png`
- `questions.json`
- `static/images/sample18.png`

## Added / removed files

None.
