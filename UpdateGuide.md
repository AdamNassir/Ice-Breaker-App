# Completed update — direct Bitcoin and Mbappé article claims

- Round 5 states that Bitcoin fell 50% in twenty-four hours; round 8 states that Kylian Mbappé won the Ballon d’or. Each has a French headline, chapo and three body paragraphs.
- Both remain AI-written quiz fiction. The existing news layout, neighbouring images and other seven question records are preserved, including the LinkedIn passage and identity reveal.
- questions.json and Content.py match. Private provenance makes clear that neither the outlet nor the displayed journalist authored these fictional stories.

Modified files: questions.json, Content.py, ContentSources.md, UpdateGuide.md. No app files added or removed. Backups are in .agent/article-updates.

Validation: the update checks the nine-round/news structure, matching input/output deck/fallback and unchanged other seven records before writing. The agent tested the updater on fixtures; the full latest app was unavailable in its workspace. Run python check_project.py in your development environment and rehearse the presenter/phone views. No claim of live deployment or full-app testing is made by this report.

Redeploy manually and create a new room. Existing rooms retain their previous deck snapshot.
