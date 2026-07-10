---
name: compile-context
description: Preprocess and compile a context file into a flat human-readable document
context: fork
disable-model-invocation: false
---

Preprocess a file's `#include` chain and merge it into a single flat document.

Usage: `/context-compiler:compile-context <file.md>`

## Step 1 — Validate Input

If `<file.md>` does not exist, report "File not found: <file.md>" and stop.

## Step 2 — Freshness Check

```bash
plugins/context-compiler/.venv/bin/python3 plugins/context-compiler/compiled-is-fresh.py <file.md>
```

Its stdout/stderr message tells you what to do next. Follow it.

## Step 3 — Preprocess

```bash
plugins/context-compiler/.venv/bin/python3 plugins/context-compiler/preprocess.py <file.md> <dir>/<stem>.preprocessed.md
```

Where `<dir>` is the directory containing `<file.md>` and `<stem>` is the filename without `.md`.

e.g. `dir1/dir2/abc/file.md` → `dir1/dir2/abc/file.preprocessed.md`

## Step 4 — Merge to Human-Readable

Run `/context-compiler:compile <dir>/<stem>.preprocessed.md`.

This produces `<dir>/<stem>.compiled.md` — a clean, flat document with no layer markers.

## Step 5 — Report

```
✓ Compiled <file.md> → <dir>/<stem>.compiled.md
```
