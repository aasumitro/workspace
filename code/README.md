# code/ — the codebase(s)

Clone the actual source code here. This folder is where every agent's *code* work happens;
everything outside it is workspace coordination and knowledge.

```bash
cd code
git clone <your-repo> <name>
```

Then declare each repository in `.project/MANIFEST.yaml → repos`: path, remote, default branch, the
**surfaces** (backend, web, mobile, … with their paths and architecture docs), and the **check
commands** agents run before declaring work done.

Nothing here is ever committed from an agent session. Agents write the commit message to
`COMMIT.md` at the workspace root; the human commits.
