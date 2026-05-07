# Git hooks (tracked)

Git's per-clone `.git/hooks/` directory is not version controlled. To make hooks here travel with the repo, point git at this directory once per clone:

```bash
git config core.hooksPath .githooks
```

Verify with `git config --get core.hooksPath` — it should print `.githooks`.

Hook files must be executable (`chmod +x .githooks/<hook-name>`).

## What's here

No active hooks currently.
