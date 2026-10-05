RULES TO FOLLOW FOR THE CREATION OF AN ICE BREAKER ON THE TOPIC OF DISCERNING AI OR HUMAN CONTENT

Main goal : creation of an app/website used during an Ice Breaker, pertaining to a presentation on AI.

This is one complete creation brief. Implement the app described below, including the local question manager, deployment instructions and verification process. The actual wording, media and sources of individual questions are supplied separately and must not be invented by this file.

Functionalities :

- Connecting to the website should be simple. Use Python FastAPI for the server, Supabase PostgreSQL for deployed storage and Vercel for the website. Use plain HTML, CSS and JavaScript for the interface, such that the code remains readable and easy to modify.

- Detail all downloads and installs in ReadMe.md. The user must be able to follow the instructions on Windows, Linux and macOS without guessing missing commands. Include Python 3.12, virtual environments, pip, local startup, Supabase setup, Vercel deployment and how to stop/restart the app.

  Necessary local setup, Windows :

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

  Necessary local setup, Linux and macOS :

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

  Explain any PowerShell activation restriction and an alternative using the virtual environment's Python executable. Explain that localhost on a phone points to the phone; local phones need the laptop's LAN address and a reachable network. A Vercel HTTPS URL is the normal event entry point.

- The Ice Breaker should resemble a game. Players enter a room code, choose a unique pseudonym and join from their phone. They must not need a Supabase account, Vercel account, email address or player password. The presenter can be protected by a server-configured presenter password.

- Answering should remain simple : AI OR HUMAN. There are exactly two voting choices in every scored round. Content changes between rounds; the controls stay consistent. Each player can vote once per round. A vote cannot be changed or accepted after the server deadline.

- Track player score, streak and rank on their phone. Track all scores on the server. The presenter must not have a leaderboard/sidebar during questions or reveals. Show the complete rankings only after the final round.

- The app must initially open on the appropriate route : `/` for players and `/presenter` for the presenter. Keep the roles separate. Explain these URLs clearly in ReadMe.md. Do not require players to log into a hosting dashboard.

- A QR code should be created automatically by the app. It must open the deployed player URL with the room code already filled in. Generate the QR modules on the server and draw them in a canvas with code. Do not rely on a third-party QR service or a fragile image-load event. Show an intelligible error and a working Retry button if creation fails. Keep Copy player link available.

- The first presenter screen after room creation must show a large, centered QR code. No question is visible yet. Do not show a QR code beside questions once the game starts.

- The presenter clicks Start round 1 when players have joined. The question immediately appears on the projector and on phones, and its countdown starts.

- The presenter selects one duration for the entire game before starting it. Allow 5 to 120 seconds, in increments of 5. Respect that value in every round. Legacy question-level seconds fields must not override it.

  Required timer logic, inside a locked room transaction :

```python
state["duration"] = state["default_seconds"]
state["deadline"] = time.time() + state["duration"]
state["phase"] = "live"
```

- When the timer ends, the answer is revealed. Players cannot vote during the reveal. The presenter decides when to advance; a reveal must not automatically disappear or advance to another question.

- After a reveal, clicking Next round must immediately start the next question and a fresh full countdown. Do not require an additional Start click between rounds. Pressing Enter must perform the same action as Next round. Ignore held/repeated keys and protect against rapid or duplicate requests. Preserve normal keyboard behaviour inside form fields and unrelated controls.

  Required next-round logic :

```python
if state["index"] == len(state["rounds"]) - 1:
    state["phase"] = "finished"
else:
    state["index"] += 1
    state["votes"] = {}
    state["duration"] = state["default_seconds"]
    state["deadline"] = time.time() + state["duration"]
    state["phase"] = "live"
state["revision"] += 1
```

  Validate the requested revision before doing this. Keep the operation atomic. A duplicate request must not advance twice or start two rounds.

- The server is authoritative for time, votes, answers, scoring and state transitions. Browser clocks can be inaccurate, so calculate the displayed countdown from the server deadline and a monotonic browser clock. Reject late votes server-side even if a player's screen has not refreshed yet. Scoring must happen exactly once per reveal.

- Add streaks, it is supposed to be ludic after all. Correct answers give 100 points. Add 25 points for each additional consecutive correct answer, capped at 100 bonus points per round. Incorrect or missed answers reset the streak. Keep the formula in editable server constants, but do not display an explanation of the formula in the public game.

- Each normal question must show a descriptive, neutral title that names what is shown, rather than an enigmatic phrase, and a short introduction above its content on the presenter and phone. Use the existing title and context fields. Do not reveal its origin, source, difficulty or discussion prompt before voting ends. Do not tell players which people or details to inspect in a painting; introductions must not hint at hidden additions. For a conversation, state exactly which reply players judge. Keep text compact and centered. For code questions, imply the usage scenario through table, column, variable or filter names. A supplied SQL example may include readable comments, joins across tables, CTEs and pivot-style aggregation; the short introduction must not narrate a separate scenario. Show no round title or introduction in the first QR lobby or presenter final rankings.

- On reveal, show AI or HUMAN. Do not display explanation paragraphs, technical notes, suggested discussion questions or text telling the presenter to discuss/continue. Keep those notes available to the author in the manager and private source files.

- For configured real photographs, the reveal may also show a concise caption stating what the image is, its date and its source link. For explicitly configured HUMAN text excerpts, show concise source labels, publication dates and links only after reveal. Do not add discussion or explanation paragraphs. Apart from their neutral title and short voting introduction, do not add contextual text to social posts or code cards at reveal. For an image with a configured hidden-character highlight, show a red circle only after reveal. Transform and scale the circle together with the image.

- Do not expose answer keys, explanations, source notes or reveal-only highlight coordinates in a live question payload. Keep Content.py, questions.json and source notes outside static/. Do not create a public API that returns the full saved deck.

- Once all rounds have been gone through, the presenter uses the same advance control or Enter to show final results. Use a tournament-style podium, medals for places 1-3 and ordinary placement numbers below them. Preserve sensible tied rankings. Show only placement, pseudonym and score in the rankings; no explanatory or scoring text.

- Have confetti come out of the occupied podium places. Run a short burst once per room rather than repeating it at every poll. Respect reduced-motion preferences. The presenter remains on the final results screen and has no bonus navigation afterward.

- On phones, add an unscored question after the final rankings : "Was this game made with AI or not ?". It has AI and HUMAN buttons. Either choice reveals AI. This must not change the score, send a scored vote or advance the presenter. Preserve the phone's bonus reveal through polling and rerenders.

- After that AI reveal, show an ordered explanation of the development workflow on the player's screen. Also support the same explanation on the standalone `/bonus` page. Keep this workflow hidden until the bonus has been answered. The presenter must still remain on rankings.

  Presentation sequence :

  1. I supplied one large instruction file to the agent.
  2. The agent created the app. I configured the agent to test its output, so it cyclically built, tested, fixed problems and tested again before delivering an output.
  3. I went into the code and tested the app myself, including the presenter and phone experience.
  4. I set up the question manager, added instructions for generated content and supplied sources for real content.
  5. I wrote requested changes in UpdateGuide.md and saved it. The agent read the saved request, made changes and tested, then replaced my request with a report of what it had done.
  6. I verified that report, tested again and repeated the loop for further changes.

  Call the assistant an agent throughout this explanation. Present the sequence as an illustrative reconstruction of the development workflow. Do not claim it is a literal transcript or exact chronology. Keep the coding agent separate from the deployed game. Saving UpdateGuide.md triggers it only while the local agent_watch.py process is running. The actual history remains separate from this illustrative sequence.

Appearance and restrictions :

- Use blue and red with white and neutral backgrounds. Include LogicLever and TotalEnergies logos without redrawing or recoloring them. Put both logos prominently in the center of the player/presenter opening panel, replacing the large app title, introductory sentence and feature pills. Preserve every edge and the complete tagline, using natural aspect ratios and contain framing. Blend a white-backed wordmark into tinted page surfaces with CSS so it does not appear as a contrasting rectangle; retain the original logo file. If the supplied original is already clipped, use the complete official asset and record its source privately. Use LogicLever’s blue for the second voting choice, focus indicators and secondary accents; use red for the first choice and primary actions. Metallic medal colors may remain limited to final podium decoration. Keep the interface responsive for phones and a large projector. Make question content centered and use the width freed by removing QR/ranking sidebars. Avoid unnecessary text and visual hints about an answer.

- For editable news text, support `text_style: "news"` alongside backward-compatible `"plain"`. The articles must be in French, so use the selected French publication’s complete website page as the layout reference. Implement the page in native HTML/CSS with its actual logo asset, French navigation, headline/chapo/byline arrangement, main article, sidebar, related stories and footer. Do not substitute a cropped article screenshot for the website. Record the exact primary references in LayoutSources.md and state any unverified pixel/font matching honestly. Never claim the invented story actually appeared in the referenced outlet. Share the renderer between the game and manager preview. Treat the first paragraph as headline, the next as chapo and remaining blank-line-separated paragraphs as body. Render all question text safely with textContent, never HTML. Bound the page height, make the entire embedded page scrollable on phone/presenter and adapt to its container width. Keep voting accessible and the authoritative timer running. Preserve the reader’s scroll position through polling and reveal, then reset it for a different article. Outer controls, neutral titles and introductions remain English. Maintain news presentation for specifically identified legacy bundled articles saved before the format flag, including old room snapshots. Preserve ordinary/custom plain text and do not rewrite saved room content as a side effect. Validate asset loading through the actual shipped HTML as well as isolated DOM checks.

- Do not display the following public passages, or paraphrases that simply put them back : join-on-your-phone prose below the question, scanning/pseudonym instructions under the presenter QR, the points/streak calculation, discussion instructions, player introductory copy about posts/text/images, feature pills about rounds/choices/streak bonuses, or presenter introductory copy about setting the pace and making the call.

- Players must be able to inspect images on their phone : pinch to zoom, drag while zoomed, double-tap to zoom/reset, and use +, minus and Reset buttons. Support keyboard equivalents where practical. Bound panning and zoom, preserve aspect ratio and keep the reveal circle aligned. Preserve zoom/position on polling and reveal; reset for a new question. Do not block voting or pause the timer. Scrolling outside the image should still move the page.

- Any social UI reconstruction must match its supplied reference rather than using a generic card. Anonymize displayed identities as requested. The French Macron post must show an unblurred name, handle and profile photograph. Keep LinkedIn and Teams identities anonymized. When coarse pixelation is required for other content, name and handle must actually become unreadable. Do not use a weak cosmetic blur that leaves the identity visible. These are authoring/layout requirements; individual post wording belongs in the separate content deck.

Question manager :

- Create a separate local question manager, runnable with `python question_manager.py`. It must not be part of the public Vercel player interface. Bind it locally and protect mutation requests with a manager token and origin/host checks.

- The user should be able to add text, code/commit snippets, images, audio and video. Image/audio/video questions need working file-upload controls, not just a text field. Support documented HTTPS recording/video links and supported YouTube clips, including start/end offsets, for custom questions.

- The default event deck should have nine image/text questions. Keep the app interface, question titles and short introductions in English; the news articles, Macron post and Teams messages are explicitly in French. Replace default prose excerpts with plausible, amusing AI-written fictional news articles, include an unusual authentic sports photograph, and make the Teams manager reply less technical and clearly the object of classification. Store provenance and fictional status privately; never claim invented news or a parody post is an authentic external source. Do not include audio or video in that default deck. Media support remains available in the manager for custom decks. The actual ten questions and their origins are supplied separately; do not reproduce or invent them in this creation brief.

- Save the managed deck as questions.json, keep a matching Content.py fallback and read the saved JSON first. Both files must be included in the complete ZIP. Upload media into the correct static subfolder and keep original source files outside the public app where appropriate.

  Deck envelope :

```python
deck = {"schema_version": 1, "rounds": supplied_questions}
```

  Question fields supported by the shared parser :

```python
# Schema outline; values are supplied by the author, not by this brief.
question = {
    "title": neutral_title,
    "kind": "image",          # text, code, commit, image, audio or video
    "media": local_media_path,
    "alt": neutral_description,
    "image_fit": "contain",
    "answer": known_origin,   # exactly AI or HUMAN
    "context": author_context,
    "text_style": "plain",    # text rounds: plain or news; defaults to plain
    "explanation": private_answer_notes,
    "source": private_source_notes,
    "source_url": source_url,
    "reveal_sources": [],     # opt-in HUMAN text credits: {"label": source_label, "url": https_url}
}
```

- Validate saves before replacing the deck. Reject unsupported media, invalid paths, traversal, malformed content and bad highlight coordinates or malformed reveal-source links. Preserve optional reveal-source credits through manager saves. Keep a backup on save, and detect conflicting editor revisions. Allow the manager to open and repair a deck with missing media or malformed JSON instead of trapping the user behind an error.

- A new game room must take a snapshot of the saved deck. Existing rooms must not silently change questions when the author saves a different deck. Provide clear missing-media/deck errors, a working Reload saved control and exact deployment instructions for new media.

- Write HowToAddImages.md and QuestionManager.md. Clearly identify which paths, CSS rules, image-fit/position fields and authoring constants should be edited. Visible UI and user-facing documentation must be in English, with the specified French question-content exceptions. Title and short introduction are public; explanation and source notes remain private until an authorized reveal.

Supabase and Vercel :

- Use a private schema and a restricted application database role. Provide an initial supabase.sql migration and explain running it once in Supabase's SQL Editor. Explain transaction-pooler credentials, the role-qualified username and password URL encoding. Do not expose the private schema through the Data API.

- Supabase is server storage, not a player login system. Store DATABASE_URL and PRESENTER_PASSWORD only on the server. Do not substitute an API URL or browser anon key for the PostgreSQL URI.

  Environment variables, placeholders only :

```dotenv
DATABASE_URL=postgresql://icebreaker_app.PROJECT_REF:URL_ENCODED_APP_PASSWORD@YOUR_POOLER_HOST:6543/postgres
PRESENTER_PASSWORD=YOUR_PRESENTER_PASSWORD
PUBLIC_BASE_URL=https://YOUR_DEPLOYMENT.vercel.app
```

- Keep .env out of Git and ZIP deliveries. Provide .env.example. Use TLS, transaction-compatible connection settings and a locked state transaction. A local SQLite fallback is acceptable for development; do not silently use local SQLite for multi-instance Vercel production rooms when Supabase is missing.

- Export the FastAPI `app` from main.py and use the project's native Vercel FastAPI configuration. Keep requirements.txt readable plain text containing actual Python requirements. Do not put Markdown fences, formatting markup or broken include paths inside it. Document the correct repository/root directory to deploy.

- The deployment URL must be publicly reachable by participants. Explain Vercel deployment protection where relevant, and the distinction between project administration and visiting a public website. No Vercel account is required for a player on an accessible deployment.

- Include a health check which reports database availability without returning secrets. Do not expose server tokens or personal credentials in logs, player state, QR code payloads or browser JavaScript.

Instructions given to the agent :

- Treat this creation brief as the required app specification. Implement it as a complete project. Do not stop at a plan, mock-up or partial set of disconnected files.

- Before returning an output, test the code it contains. Use an iterative loop : implement, run meaningful checks, inspect failures, fix problems and rerun the affected checks. Testing must validate observable behaviour; do not merely assert that a function returns the values it just assigned.

  Validation-loop outline, instructions to the agent rather than a standalone program :

```python
request = read_saved_request("UpdateGuide.md")
implement(request)
while failures := run_relevant_checks():
    fix(failures)
write_completed_report_if_request_unchanged("UpdateGuide.md")
```

- Cover game timing, full scoring, duplicate/stale/late votes and controls, authentication, QR creation, source secrecy, deck/media consistency, question-manager upload/save/repair and room snapshots. Check player image gestures, keyboard advancement, final placements, bonus persistence and workflow visibility. Visually inspect created media and changed layouts when possible. Clearly state any browser, deployment or load-test limitation.

- Never describe the app as error-free merely because tests passed. Report what was actually tested. Do not claim a live Supabase/Vercel deployment, an active file watcher or physical-phone testing unless it was actually performed.

- Include a real local agent_watch.py process using authenticated Codex CLI. Watch UpdateGuide.md saves with a debounce; ignore completed reports, drafts, blank files and identical already-attempted requests. Keep one watcher per repo. Use workspace-write permissions, no bypass flags, argument lists and stdin rather than shell interpolation. Add native Windows startup/login instructions and a StartAgent.cmd launcher. The deployed game must not start this process.

- Snapshot each request and source checkpoint before editing, excluding credentials, dependencies and runtime files. Give the agent the creation brief, AGENTS.md and request; it may implement/test/fix locally but must not edit UpdateGuide.md or the protected watcher/config/check gate. Run independent Python and frontend checks afterward, feeding failures back for a bounded maximum of three attempts. Preserve incomplete requests, logs and checkpoints on failure; allow an explicit retry. Stop launched processes on timeout or Ctrl+C.

- When agent work and independent checks succeed, the watcher replaces the pending request with a report containing resulting behaviour, exact actual modified/added/removed files and validation. If the author saved newer request text during the run, preserve it and put the old report in the run directory instead. Keep deployment manual. Document actual authenticated-model, Windows, browser and deployment testing limits separately from the presentation narrative.

- The human author must be able to inspect the report, review the code and test again. Keep the update loop easy to repeat. AGENTS.md should tell future agents to read this creation brief and UpdateGuide.md before editing.

- Preserve question content and media unless the pending request explicitly changes them. Do not introduce unrelated authoring tools. Never publish source credentials or private data. Any genuinely destructive or externally irreversible action must follow the user's authorization and available approval rules.

Folder structure :

- Ice_Breaker_Game_App/
  - CreationInstructions.md : this complete creation brief, with no individual question content.
  - AGENTS.md : repository working instructions for the agent.
  - ReadMe.md : install, local operation, Supabase and Vercel instructions for all three operating systems.
  - UpdateGuide.md : pending human change requests, subsequently replaced by the validated completion report.
  - agent_watch.py, agent_config.json and StartAgent.cmd : local watcher, configuration and Windows launcher.
  - AgentSetup.md and AgentRequestTemplate.md : installation/login, operation, retry/recovery and drafting template.
  - check_project.py and tests/frontend/ : independent Python/DOM check gate, scripts and development-only npm dependencies.
  - .agent/ : ignored local run requests, checkpoints, logs, lock and reports; never deliver this runtime folder.
  - Verification.md : actual checks and limitations.
  - HowToAddImages.md and QuestionManager.md : authoring instructions.
  - Content.py and questions.json : separate default/fallback and managed decks.
  - ContentSources.md : private answer notes and credits.
  - main.py, store.py and question_content.py : game API, storage and shared validation.
  - question_manager.py and manager_assets/ : separate local editor.
  - requirements.txt, requirements-dev.txt, .env.example, supabase.sql and vercel.json : setup/configuration.
  - static/index.html and static/presenter.html : player and presenter screens.
  - static/app.js, static/media.js and static/imagezoom.js : game, playback and image inspection.
  - static/bonus.html, static/bonus.js and static/workflow.js : unscored reveal and development sequence.
  - static/style.css and static/imagestyle.css : clearly editable presentation rules.
  - static/branding/ : supplied logos and the complete official logo asset.
  - static/newsarticle.js and newsarticle.css : shared editable news presentation.
  - static/images/, static/audio/ and static/videos/ : published media.
  - tests/ : meaningful regression checks.

Modify the structure by adding or moving files only when needed; explain every such change. Keep private documentation and decks outside static/. Keep local runtime files, secrets, caches and test dependencies out of the ZIP.

The needed result out of this prompt should be a complete folder with the functioning app/website, supplied content files, a local question manager and the instructions required to use it through Supabase and Vercel. Whenever an updated ZIP is provided, list all modified, added and removed files. Verify that the ZIP actually contains the files it claims to include and that the extracted project matches the tested project.
