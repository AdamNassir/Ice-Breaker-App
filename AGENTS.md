# Repository instructions for the agent

Read `CreationInstructions.md`, the saved `UpdateGuide.md`, and `Verification.md` before editing. The creation brief is a consolidated specification, not an exact development transcript. Individual question content is in `questions.json`, `Content.py` and the private source notes.

1. Treat the user's current request and any saved pending change in `UpdateGuide.md` as the change scope. A completed report in that file is not a new request. If a required behaviour is unclear, investigate the code and continue work that is independent of the ambiguity.
2. Preserve the supplied deck/media unless changing them is requested. Maintain JSON/fallback equivalence when a deck change is authorized. Do not expose private notes or answer fields in live payloads.
3. Implement, run relevant checks, fix failures and rerun affected checks until the result is ready for human review. The repository uses `python -m unittest discover -s tests -v`. Frontend checks must cover the changed behaviour; syntax checking alone is insufficient. Document browser/phone/deployment testing limitations honestly.
4. Keep server timing and scoring authoritative, room changes atomic, the first QR lobby intact, Next/Enter immediately starting subsequent rounds, and presenter rankings free of the phone-only bonus/workflow.
5. After completing and verifying a saved request, replace it in `UpdateGuide.md` with a reviewable completion report. List resulting behaviour, exact modified/added/removed paths, check results and install/redeploy steps. Do not silently erase an unfinished request. The user then reviews/tests and may replace the report with another request.
6. This is an agent-session workflow. The game has no autonomous agent or file watcher. Saving `UpdateGuide.md` alone does not trigger execution; a running agent session must read it. Never claim an absent watcher is implemented.
7. Keep `.env`, tokens, database files, caches, runtime installations and private source material out of deliveries. Do not publish or deploy unless authorized. A requested reversible local change and ZIP delivery do not require another confirmation.
8. Before a ZIP delivery, compare the project with the previous release, verify the exact archive manifest and check a fresh extraction. Return the complete ZIP and exact changed-file list.

Use plain English. Call the assistant an agent in the app's illustrative workflow. Keep actual verification separate from the illustrative narrative.
