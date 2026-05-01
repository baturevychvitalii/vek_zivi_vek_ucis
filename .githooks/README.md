# Git hooks (tracked)

Git's per-clone `.git/hooks/` directory is not version controlled. To make the hooks here travel with the repo, point git at this directory once per clone:

```bash
git config core.hooksPath .githooks
```

Verify with `git config --get core.hooksPath` — it should print `.githooks`.

## What's here

- `post-merge` — fires after `git merge`/`git pull`. When the merge lands on `master` or `main`, it runs `.claude/scripts/mem-bank-graduate.py` to graduate the merged branch's `active-context.md` into a durable entry under `.claude/meta/architect/why/`. Merges in the other direction (master → feature) are ignored.
