# AI or Human? — Ice Breaker Game

A complete browser game for an AI presentation: a presenter opens a room, players join on their phones with pseudonyms, and everyone decides **AI OR HUMAN**. The default deck has **10 rounds**: 2 commits, 2 code snippets, 4 images, and 2 short texts, split evenly between AI and human origins.

## 1. Necessary downloads and installs

| Item | Local game | Supabase + Vercel deployment | Download / account |
| --- | --- | --- | --- |
| Python **3.12** with pip and venv | Required | Recommended for rehearsal | https://www.python.org/downloads/ |
| Modern browser | Required | Required on presenter and players' devices | Chrome, Edge, Safari or Firefox |
| Python packages | Required | Vercel installs them from requirements.txt | `python -m pip install -r requirements.txt` |
| Supabase account + project | Optional | Required | https://supabase.com/ |
| Vercel account | Optional | Required | https://vercel.com/ |
| Git + GitHub account | Optional | Needed for the dashboard/Git route | https://git-scm.com/downloads and https://github.com/ |
| Node.js LTS + Vercel CLI | Not required | Only for the alternative CLI route | https://nodejs.org/ then `npm install -g vercel` |
| Editor | Recommended | Recommended | VS Code or any text editor |

No Supabase CLI, Docker, local PostgreSQL, Node build system, paid AI API key, or frontend framework is needed. All four images are bundled. Supabase is used as PostgreSQL storage through **server-side psycopg**, so there is no Supabase browser SDK or exposed database key. This project does not use Supabase Auth: pseudonyms and random game tokens are sufficient for an ice breaker.

The delivered folder is the project root. Commands below run **inside `Ice_Breaker_Game_App`**. The app works immediately with a local SQLite file; cloud deployment requires your own Supabase and Vercel setup. Credentials are intentionally absent.

## 2. Operating the app on Windows, Linux and macOS

### Windows (PowerShell)

Install Python 3.12 from python.org and enable the installer option to add Python to PATH. Extract the ZIP, then open PowerShell in the parent directory:

```powershell
cd Ice_Breaker_Game_App
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000
```

These commands do not require activating PowerShell scripts or changing execution policy. If `py` is unavailable, use `python` after confirming `python --version` is 3.12. Allow Python through Windows Firewall on your **private** event network when prompted.

### Linux (Bash; Ubuntu/Debian example)

Install Python 3.12, pip and venv using your distribution's package manager. If your distribution already provides Python 3.12:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
cd Ice_Breaker_Game_App
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

If `python3 --version` is not 3.12, install 3.12 using your distribution's supported instructions and use `python3.12 -m venv .venv`. Dependency pins were verified on Python 3.12; do not assume every future Python release is compatible. Other Linux distributions use their own package managers.

### macOS (Terminal, zsh or Bash)

Install Python 3.12 using the python.org macOS installer. Then:

```bash
cd Ice_Breaker_Game_App
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Allow incoming Python connections if the macOS firewall asks. Using an explicitly installed Python avoids dependence on an Apple-managed system interpreter.

### Start, stop and reopen

Open **http://localhost:8000/presenter** on the presenter's computer. Players use **http://localhost:8000/** only if playing on that same computer.

For phones on the same Wi-Fi, find the presenter's LAN IP:

| OS | Command / location |
| --- | --- |
| Windows | `ipconfig` → IPv4 address on the active Wi-Fi/Ethernet adapter |
| Linux | `hostname -I` or `ip address` → address on the active LAN interface |
| macOS | System Settings → Network → active connection → Details → TCP/IP |

If it is `192.168.1.42`, phones open **http://192.168.1.42:8000/**. Before starting the server, set `PUBLIC_BASE_URL=http://192.168.1.42:8000` in `.env` so the shared player link works on phones. `localhost` on a phone refers to the phone, not the laptop. Devices must be on a reachable LAN; guest Wi-Fi often blocks device-to-device traffic. HTTPS on Vercel is the easiest event option when participants are on different networks.

Stop with **Ctrl+C**. To restart, run the same uvicorn command; reinstalling is unnecessary. Local scores persist in `game.sqlite3`. To edit Python during development, add `--reload`; avoid reloading code during the actual event. Never combine `--reload` with a cloud deployment command.

## 3. Supabase setup

1. Create a Supabase project. Save its database password privately.
2. Open `supabase.sql` in an editor. Replace `REPLACE_WITH_A_STRONG_DATABASE_PASSWORD` with a new password for the restricted `icebreaker_app` database role. Avoid single quotes in this password, or escape them as `''` in SQL.
3. Run the edited SQL **once** in Supabase's SQL Editor as `postgres`. It creates a private schema, one room table, a least-privilege application role, and a row-level-security policy scoped to that role. Keep the `icebreaker` schema outside the Data API's exposed schemas. The SQL is an initial migration, not a repeatedly runnable reset script; rerunning its role/policy creation reports “already exists.”
4. Click **Connect** in the Supabase dashboard and select **Transaction pooler**. Copy the PostgreSQL URI, usually using port **6543**. Use the actual host and project reference shown by Supabase.
5. Change its username from `postgres.PROJECT_REF` to `icebreaker_app.PROJECT_REF`, and use the application-role password from step 2. The database name remains `postgres`.
6. Add this to local `.env` for a cloud-storage rehearsal, or to Vercel's environment variables for deployment:

```dotenv
DATABASE_URL=postgresql://icebreaker_app.PROJECT_REF:URL_ENCODED_APP_PASSWORD@YOUR_POOLER_HOST:6543/postgres
PRESENTER_PASSWORD=choose_a_long_random_presenter_password
PUBLIC_BASE_URL=https://your-actual-project.vercel.app
```

This is a shape example, not a working connection string. URL-encode reserved password characters such as `@`, `:`, `/`, `?`, `#` and `%`; do not URL-encode the entire URI. `DATABASE_URL` is a **server secret**. It is not the project API URL, anon key, publishable key or service-role key. Do not paste secrets into HTML, JavaScript, `Content.py`, chat, or source control. `.env` is ignored by Git.

The app connects over TLS with `sslmode=require`, uses `prepare_threshold=None` for transaction-pooler compatibility, and closes each connection after its transaction. For certificate verification beyond TLS encryption, add `sslrootcert` and use `sslmode=verify-full` in `store.py` according to your deployment's trusted CA configuration.

Open `/api/health` after configuring the database. It must report `status: ok` and `storage: Supabase PostgreSQL`. This endpoint checks connectivity and table access; it never returns credentials.

## 4. Deploy on Vercel

The implementation follows Vercel's native FastAPI deployment: `main.py` exports `app`. There is no separate frontend build or WebSocket server. Do not add an old `@vercel/python` catch-all configuration on top of this one.

### Recommended: Git + dashboard

1. Commit this folder's contents to a **private** GitHub repository. Check that `.env`, `.venv`, SQLite files and credentials are excluded. A public source repository would expose `Content.py` and the game answers to curious participants.
2. In Vercel, choose **Add New → Project**, import the repository, and select the project root. If the repository contains a parent folder, set **Root Directory** to `Ice_Breaker_Game_App`.
3. Use the **FastAPI** framework preset/detection. Leave build and output-directory overrides unset. Let Vercel install from `requirements.txt` (which uses `constraints.txt`). Use Python 3.12 in the project's Python runtime selection/configuration where available.
4. Set `DATABASE_URL` and `PRESENTER_PASSWORD` as production environment variables **before deploying**. `PUBLIC_BASE_URL` is optional: use the real production URL, or leave it unset so the request URL is used. Do not use `localhost` for the deployed app. Only add Preview values if you deliberately want preview builds to access that database; a separate Supabase project is preferable for testing.
5. Deploy. Open `https://YOUR-URL/api/health` and check storage. Then open `/presenter`, enter your presenter password, create a room and test from a phone.
6. Ensure the production URL is reachable without a Vercel login for your audience. Inspect the project's **Deployment Protection** settings if a phone sees a sign-in screen. Retain protection on previews where appropriate. The app itself requires a room token for game state and the presenter password to create a room.
7. After changes to files or environment variables, **redeploy**. Create a new room to use new content. Existing rooms retain a snapshot of their original deck.

### Alternative: Vercel CLI (all three OSes)

Install Node.js LTS, then run from the project folder:

```bash
npm install -g vercel
vercel login
vercel link
vercel env add DATABASE_URL production
vercel env add PRESENTER_PASSWORD production
vercel deploy --prod
```

Each `env add` prompts for the secret rather than putting it into command history. Optionally run `vercel env add PUBLIC_BASE_URL production` once you know the URL and redeploy. Vercel's FastAPI documentation specifies CLI **48.1.8 or later**; use an up-to-date CLI. You do not need the CLI if using the dashboard route.

**Cloud limitation:** SQLite is deliberately disabled when `VERCEL` is set. Vercel functions cannot use a local file for reliable shared state. Missing `DATABASE_URL` or `PRESENTER_PASSWORD` returns a setup error instead of silently creating ephemeral games.

## 5. How to run the ice breaker

1. Open `/presenter` on the screen you will project. Create a room, choose a title and a default timer (5–120 seconds; 25 by default). Enter the presenter password if configured.
2. Show the room code or copy the player link. Players open `/`, enter the code and choose unique pseudonyms. No account or email is required.
3. Click **Start round 1**. Content appears on both the projector and every phone, and the server deadline begins. The player has exactly two choices: **AI** or **HUMAN**.
4. The first accepted vote is final. The presenter sees the count of answers; individual choices and the correct answer stay hidden during voting.
5. When the timer reaches zero, the server rejects late answers and reveals the origin, source note and explanation. Scores update on both views.
6. Discuss briefly, then click **Next round**. The new round remains hidden in the “ready” phase until you click **Start round N**. There is no automatic advance or early reveal.
7. After round 10's reveal, click **Show final results**. Both screens show final standings; each phone also shows its own score, rank and accuracy.

Reconnect by refreshing the same tab/browser. A player's random token lives in local browser storage; the presenter's token lives in session storage and survives a refresh in that tab. Tokens never appear in the shared link. Keep the presenter tab open and do not share its stored credentials. Clearing storage, using another browser or an incognito window creates a new identity; scores cannot be recovered by pseudonym alone. Players may join an ongoing game and begin scoring in the active round if its deadline has not passed. Tied scores share a rank; names determine display order within a tie.

The room expires **12 hours after creation**. New rooms opportunistically remove expired rows. For scheduled/manual retention cleanup, run the SQL comment at the end of `supabase.sql`. A game does not have an always-running scheduler: the first API request after a deadline commits the reveal exactly once. With the default polling, active screens see it within approximately **1.5 seconds** plus network latency. If every tab is closed, the deadline still holds; the state settles when someone returns.

## 6. Scoring and modifications

| Consecutive correct answer | Points for that round |
| --- | --- |
| 1st | 100 |
| 2nd | 125 |
| 3rd | 150 |
| 4th | 175 |
| 5th and beyond | 200 |

An incorrect or missed answer awards 0 and resets the streak. There is no speed bonus, so fast connections do not earn extra points. A perfect ten-round game earns **1,750** points.

| Change | File / symbol |
| --- | --- |
| Round text, origin, source, image or audio | `Content.py` → `ROUNDS` |
| Add/remove/reorder rounds | Add/remove/reorder dictionary entries in `ROUNDS`; UI count updates automatically |
| Override one round's timer | Add `"seconds": 40` to that round |
| Point and streak rules | `main.py` → `BASE_POINTS`, `STREAK_STEP`, `MAX_STREAK_BONUS` |
| Room lifetime / player cap | `main.py` → `ROOM_LIFETIME_HOURS`, `MAX_PLAYERS` |
| Red/orange/white/gold palette | `static/style.css` → `:root` variables |
| Image size, framing and positioning | `static/imagestyle.css` and per-round fields; see `HowToAddImages.md` |
| Player interface | `static/index.html` |
| Presenter interface | `static/presenter.html` |
| Shared browser behavior / polling | `static/app.js` |
| Database transactions | `store.py` |

After changing scoring constants, also update the scoring note in both HTML files. Make changes between events: Python/JS changes need a restart/redeploy, and content changes need a **new room**. Text and code are rendered as text, never HTML or executable code. Only files in `static/` are public; do not put answer keys or credentials there. Asset filenames are neutral to avoid revealing answers in network requests.

Audio playback is supported but no recordings are bundled. Interesting replacements for technical audiences: a real versus generated release note, a terse versus polished PR review, a synthetic voice versus a consenting colleague's reading, or a generated architecture explanation versus an old public specification excerpt. Use recordings you own or have permission to share. Keep the wording identical for voice comparisons to test the audio rather than the script. A typical audio round needs a longer timer and a presenter click on the audio control; browser autoplay is intentionally not used.

This is a perception game, not an AI detector. Labels describe known origin, not quality, truth or “AI assistance” in general. The historical examples are intentionally verifiable; replace recognizable samples with your own documented human originals to increase difficulty. Preserve a source/prompt and label mixed-origin material explicitly rather than inventing a binary ground truth.

## 7. Folder structure

```text
Ice_Breaker_Game_App/
  ReadMe.md
  HowToAddImages.md
  ContentSources.md
  Content.py
  main.py
  store.py
  supabase.sql
  requirements.txt
  requirements-dev.txt
  constraints.txt
  vercel.json
  .env.example
  .gitignore
  static/
    index.html
    presenter.html
    app.js
    style.css
    imagestyle.css
    images/sample03.jpg, sample04.jpg, sample09.jpg, sample10.jpg
    audio/README.md
  licenses/CPython-LICENSE.txt
  tests/test_game.py
  Verification.md
```

## 8. Verification and troubleshooting

Install optional verification dependencies and run:

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

Use `.venv/bin/python` on Linux/macOS or `.\.venv\Scripts\python.exe` on Windows if the environment is not activated. Tests use temporary SQLite storage and do not need a Supabase account.

| Symptom | Check / resolution |
| --- | --- |
| Cannot create a hosted room | Configure both production secrets; redeploy; inspect `/api/health` |
| Database unavailable | Confirm transaction-pooler host, port, URL-encoded app password, custom username and project status; ensure SQL migration ran |
| Role or policy already exists | Initial SQL already ran; do not rerun creation statements; inspect existing role/table/policy |
| Phones cannot reach laptop | Correct LAN IP, same Wi-Fi, firewall, no client isolation; use Vercel if event Wi-Fi blocks peers |
| Vercel sign-in required | Review Deployment Protection for the production URL |
| Pseudonym taken | Use another name or reopen the original browser session |
| Content changes not visible | Restart/redeploy, then create a new room |
| Image missing | Check exact case-sensitive path and extension in Content.py and static/images |
| Timer reads zero before reveal | Network/polling delay; votes remain server-protected; do not advance until reveal appears |
| Scores don't survive Vercel request | Confirm health says Supabase PostgreSQL, not a local demo |

The hard player cap is 200, but that is an abuse/storage bound, **not a verified throughput guarantee**. All participants poll and each room has one locked database row. Rehearse on your actual Vercel/Supabase plan with the intended audience size, and monitor function/database usage. Large events may need a normalized schema and a push transport. This starter has no identity verification or multi-account prevention; participants can rejoin under new names, which is acceptable for a casual ice breaker.

## Official references (checked October 2, 2026)

- Vercel FastAPI entrypoint, deployment, static files: https://vercel.com/docs/frameworks/backend/fastapi
- Supabase connection modes and transaction pooler: https://supabase.com/docs/guides/database/connecting-to-postgres
- Supabase psycopg prepared-statement setting: https://supabase.com/docs/guides/troubleshooting/disabling-prepared-statements-qL8lEL
- Content provenance and licensing: see `ContentSources.md`.
