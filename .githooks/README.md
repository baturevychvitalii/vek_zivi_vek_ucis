# Git hooks (tracked)

Git's per-clone `.git/hooks/` directory is not version controlled. To make the hooks here travel with the repo, point git at this directory once per clone:

```bash
git config core.hooksPath .githooks
```

Verify with `git config --get core.hooksPath` — it should print `.githooks`.

Also enforce no-fast-forward merges so the hook always fires:

```bash
git config merge.ff false
```

Hook files must be executable. After cloning or pulling a new hook:

```bash
chmod +x .githooks/pre-merge-commit
```

## What's here

### `pre-merge-commit`

Fires before a merge commit is created. Checks whether the branch being merged (`MERGE_HEAD`) contains an ungraduated `small-bank.md`. Blocks the merge if so.

**Why:** `small-bank.md` is tracked and deleted by the graduation script (`big-bank.py`). Its presence on a branch means `/mem-bank-big-bank` was not run before merging.

To unblock: switch to the branch being merged, run `/mem-bank-big-bank`, commit the result, then retry the merge.
