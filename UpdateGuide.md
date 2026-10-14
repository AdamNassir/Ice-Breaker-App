# Completed update — team discovery and pooled team voting

## Changes

- Team-directory cards now show a team name, founder, member count, highlighted captain and member chips, responsive grid styling, and clearer Join controls. Team names and nicknames are inserted as text, not HTML.
- A round still accepts one immutable private AI/HUMAN vote per team member. On expiry the server freezes all ballots and enters a **3-second pooling phase**. The correct answer, final tally and reveal media remain unavailable until the reveal phase.
- Each registered team is one scoring participant. Strict AI/HUMAN majority sets the team's answer. A tie or no votes means abstention, earning zero points. A team's streak and score apply equally to its members; the standings and podium rank teams rather than their individual members.
- The reveal API exposes each team's answer and vote counts; the player UI confirms its team's chosen answer. Players without a team do not score in rooms with registered teams. Rooms without any teams retain the original solo-player behavior.
- Presenter and players see a pooling message and cannot advance or vote during pooling. The presenter still starts rounds, and Next starts the following round immediately after a reveal.

## Verification

- Python unit suite: **51 tests passed**, including new team majority, dissenting member, ties, frozen interim phase and team score assertions.
- `node --check` on all JavaScript sources passed.
- Full frontend DOM suite was **not executed** because npm dependencies are absent in this environment. Offline npm install reported an uncached `xmlchars` package; online installation timed out. `python check_project.py` consequently stops at its frontend dependency prerequisite.
- No device, browser, remote database or deployment checks performed.

## Install and test

Extract complete ZIP; retain your own `.env` and production database setup. Run `pip install -r requirements.txt -r requirements-dev.txt`, `npm --prefix tests/frontend ci`, then `python check_project.py`. Redeploy server and static assets and create a new room. Existing active room snapshots should not be used to assess team scoring. No schema migration is needed.

## Modified paths relative to the supplied ZIP

- `main.py`
- `static/app.js`
- `static/index.html`
- `static/presenter.html`
- `static/style.css`
- `tests/test_teams.py`
- `tests/frontend/teams.cjs`
- `UpdateGuide.md`
