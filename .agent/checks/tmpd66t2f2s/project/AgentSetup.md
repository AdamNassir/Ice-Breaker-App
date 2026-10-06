# Local saved-request agent

Run this on the computer containing your project. With the watcher running, write a request in **UpdateGuide.md** and save it. Codex edits the local code, tests it, receives failing-check output for another attempt, and replaces the request with a completion report after independent checks pass. You inspect the report and test the app, then save the next request in the same file.

The actual agent is the authenticated **Codex CLI**. `agent_watch.py` handles watching, checkpoints, checks and reports; it is not a language model. The game and question manager do not start it. Leaving the watcher terminal open keeps it active. No cloud service, scheduled ChatGPT task or Vercel process watches your Windows files.

## Windows setup — once

Open PowerShell **inside the project folder**, where main.py is. Install [Python 3.12](https://www.python.org/downloads/) and [Node.js LTS](https://nodejs.org/), then reopen PowerShell so their commands are available.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
npm.cmd install -g @openai/codex
npm.cmd --prefix tests/frontend ci
codex.cmd --version
codex.cmd login
```

Complete the login with your own Codex account. The agent uses that account's available access and usage limits; no key belongs in the repository or Vercel. The npm commands use `.cmd` so PowerShell script execution policy does not block npm/codex wrappers. The watcher resolves the npm wrapper to Node without executing request text in a shell.

Open `codex.cmd` once in this folder and complete the native Windows sandbox setup if prompted. Choose workspace permissions; exit with Ctrl+C after setup. Codex's recommended native Windows sandbox may require a one-time administrator setup. If your machine's policy blocks it, follow the official Windows sandbox troubleshooting page below rather than changing this project to unrestricted access.

Check the installation and the app:

```powershell
.\.venv\Scripts\python.exe agent_watch.py --doctor
.\.venv\Scripts\python.exe check_project.py
```

`--doctor` checks CLI version/options, saved login and local dependencies without calling a model. `check_project.py` runs Python API/manager/watcher tests, JavaScript syntax checks and the real game/manager/zoom/keyboard/workflow DOM checks against temporary local fixtures. It never needs your Supabase database.

## Start and use

Double-click **StartAgent.cmd**, or run:

```powershell
.\.venv\Scripts\python.exe agent_watch.py
```

Leave this terminal open. In your editor, replace the completed report in **UpdateGuide.md** with your request and save. Plain English works; no special request syntax is required. Example:

```markdown
# Pending update

Make the presenter timer larger on the question screen.
Keep the phone timer and the selected countdown duration unchanged.
Verify that the timer still counts down and Next/Enter still starts the next round.
```

The watcher waits for the file to settle, starts one request, and prints the run/attempt number. Full activity is recorded under `.agent/runs/`. After checks pass, open UpdateGuide.md for the exact modified/added/removed paths and validation results. Restart local game processes as needed, test the change, then deploy manually when you are ready.

Use **AgentRequestTemplate.md** if you want sections for acceptance criteria. With autosave enabled, use `# Draft update` as the first line while writing; change it to `# Pending update` and save when finished. Completed reports, drafts and blank files do not trigger work. A new pending request already on disk is processed when the watcher starts.

To stop, press **Ctrl+C** in the watcher terminal. Restarting it does not repeat an already attempted identical request. Rewriting different request text queues new work; just saving identical bytes does not.

## Failure, concurrent edits and recovery

- The default limit is **three agent attempts** per request. Failed independent checks are fed back to the next attempt. A CLI/login/quota/sandbox failure or a blocked agent stops that request instead of repeatedly consuming runs.
- On failure, the pending request remains in UpdateGuide.md. The terminal points to `.agent/runs/<run>/report.md` and logs. Changes may be partial; inspect them before continuing. Nothing is silently rolled back over your edits.
- Fix missing dependencies/login or clarify the request, then retry it explicitly:

```powershell
.\.venv\Scripts\python.exe agent_watch.py --once --retry
```

- Only one watcher may run in a project. Stop the first one before using the retry command. `--once` processes a single new request; `--status` shows the last run status without a model call.
- If you save a newer UpdateGuide.md while the agent is working, the newer content is preserved. The old run's report stays in its run directory, and the watcher processes the new request next. Avoid manually changing other source files while an implementation is in progress; only the request-file conflict is automatically checked.
- Each run keeps the original request and a `before.zip` source checkpoint. It excludes credential files, dependencies, caches and runtime databases. Stop the watcher before restoring selected files from a checkpoint; restoring is a manual review decision.
- A crash/interrupted run is not automatically rerun on restart. Review its checkpoint/logs and use the explicit retry command. Timeouts and Ctrl+C stop the launched process tree.

## Configuration

`agent_config.json` controls the command, model, debounce, attempt limit and timeouts. An empty `model` uses your own Codex default; set an available model identifier if you want to choose one. `{python}` in check arguments is replaced by the watcher’s current Python executable, so start it with the project virtual environment.

The CLI runs in foreground mode (`--no-daemon`) with **workspace-write** permissions and **never** approval prompts: actions outside its permitted sandbox fail and are reported. Foreground mode keeps the launched run attached to the watcher for cancellation. The watcher never adds unrestricted/bypass flags. It invokes argument lists directly, not shell strings. Author requests apply locally; pushing, deploying, publishing and messaging are excluded from the automatic workflow.

`agent_watch.py`, `agent_config.json` and `check_project.py` are protected validation files: the automatic agent must not change them to make its checks pass. Edit them yourself, with the watcher stopped, when intentionally changing the agent setup. Other meaningful regression tests can be added for requested app changes; do not weaken the checks to hide a failure.

The agent can read files in its project. Keep credentials out of the authoring copy; use blank/example environment settings for local tests. Logs/checkpoints remain local and are excluded from Git and ZIP releases. The validator sets local database environment overrides, and uses a temporary isolated manager copy; it does not test or deploy to live Supabase/Vercel.

## macOS and Linux

Install Python 3.12, Node.js LTS and Codex CLI, then run from this folder:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
npm install -g @openai/codex
npm --prefix tests/frontend ci
codex login
.venv/bin/python agent_watch.py --doctor
.venv/bin/python check_project.py
.venv/bin/python agent_watch.py
```

The same request, report, retry and Ctrl+C workflow applies. Node/JSDOM are development dependencies under tests/frontend; they are not required by the deployed game.

## References and verification limits

- [Official Codex CLI setup](https://learn.chatgpt.com/docs/codex/cli)
- [Non-interactive execution, authentication and structured outputs](https://learn.chatgpt.com/docs/non-interactive-mode)
- [CLI command reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- [Native Windows sandbox setup/troubleshooting](https://learn.chatgpt.com/docs/windows/windows-sandbox)
- [Official scripted Codex example using npm installation](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex)

The local CLI's command help was checked during creation. Automated watcher tests use a deterministic fake CLI to exercise real subprocesses, save detection, failed-check repair, report writing, checkpoints, locks and timeouts without paid model calls. An authenticated model run and native Windows sandbox were not tested in the creation environment. Complete login, --doctor and a small real request on your own computer to validate those parts. DOM checks do not replace a phone/projector rehearsal.
