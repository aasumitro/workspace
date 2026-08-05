# COMMIT.md — commit message handoff

Agents write ready-to-use commit messages here. **The human commits.** Newest entry on top; clear
an entry once it has been committed.

## Format

```
## #<seq> — <type>(<scope>): <subject>

<body: what changed and WHY, written for the repository's own history — no references to
plans, tasks, or this workspace, which never ship with the code. Note what was verified
(commands run, browser-tested or not) and any deliberate scope limits.>
```

Types follow the repository's existing history (conventional commits unless it says otherwise):
`feat` · `fix` · `refactor` · `docs` · `test` · `chore`. Scope is the surface or module.

---

_(no pending commit messages)_
