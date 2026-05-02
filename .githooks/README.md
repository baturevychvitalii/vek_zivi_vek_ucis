# Git hooks (tracked)

Git's per-clone `.git/hooks/` directory is not version controlled. To make the hooks here travel with the repo, point git at this directory once per clone:

```bash
git config core.hooksPath .githooks
```

Verify with `git config --get core.hooksPath` — it should print `.githooks`.

## What's here

No hooks currently configured. The directory is kept as a tracked home for any future tracked git hooks.
