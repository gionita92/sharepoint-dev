---
description: Review SPFx code against the bundled SharePoint docs, with a cited page for each finding
argument-hint: [path | diff]
---

Use the `spfx-reviewer` agent from the spfx-docs plugin to review SPFx code. Scope:

- If the argument is `diff`, review the current git diff (staged and unstaged).
- If it's a path, review that file or folder.
- If it's empty, review the whole SPFx project in the working directory.

Argument: $ARGUMENTS

Pass the agent the scope and the project directory, then show its report as it returned it.
