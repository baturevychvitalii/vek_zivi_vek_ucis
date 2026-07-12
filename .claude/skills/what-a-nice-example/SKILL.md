---
name: what-a-nice-example
description: Turn a successful run from the current session into a README example section with screenshots
disable-model-invocation: false
---

Capture a run the user liked — from this very session — as a narrated example in the
right README, with screenshots imported from the local screenshot folder.

**Usage** `/what-a-nice-example [hint: which run, or which README]`

## Identify the run

The source material is the current conversation — quote it, never reconstruct it.
Pick the run the user means (the most recent pipeline/skill run if unambiguous,
otherwise ask). Break it into 3–6 narrative beats worth showing. Prefer beats that
demonstrate trust behaviors — context awareness, deck backup, sync, the approval
gate — those are what readers evaluate.

For each beat decide: **text excerpt** (the default — searchable, copy-pasteable,
zero maintenance) or **screenshot** (only where pixels carry information text can't:
the Anki UI, a rendered card, a busy colored terminal moment).

## Resolve the target README

| Run showcases | README | Assets dir |
|---|---|---|
| anki-mcp plugin internals (feedback loop, MCP tools) | `plugins/anki-mcp/README.md` | `plugins/anki-mcp/assets/` |
| anything else — pipelines, groves, monorepo skills | `README.md` | `assets/` |

Read the target README's existing example sections first. If one already covers this
flow, propose **improve or replace** rather than adding a near-duplicate — show what
would change. Confirm the target and the add/replace decision with the user before
writing anything.

## Draft the section

House style — match "Example: feedback loop in action" in the anki-mcp README:

- Open with the concrete before-state as a fenced code block
- Narrated prose between artifacts — every image or excerpt gets a lead-in sentence
  saying what to notice, and images get descriptive alt text
- Before/after field changes go in ```diff blocks — GitHub renders red/green, colors
  without pixels
- A full transcript, if included at all, goes inside a `<details>` collapsible
- Image filenames: `<topic>-NN-<slug>.png` (e.g. `feedback-02-confirm.png`)

## Screenshots

Ask the user: already taken, or taking them now?

**Taking now** — drop a marker in the screenshot filename format:

```bash
date +%Y.%m.%d_%H:%M:%S
```

Present the numbered shot list: for each shot, what to bring on screen and which
Vscreenshot mode (usually `select`). The user captures **in shot-list order** with
`/opt/scripts/Vscreenshot` and says done.

List the captures:

```bash
ls ~/Pictures/screenshots/
```

Files whose names sort after the marker, in ascending order, are shots 1..N —
filenames are `%Y.%m.%d_%H:%M:%S.png`, so lexicographic order is chronological
order. If the count doesn't match the shot list, show the mismatch and ask.

**Already taken** — ask for the paths, oldest first, and map them to beats together
with the user.

## Import assets

Copy each capture into the assets dir under its descriptive name — one `cp` per
file, copy never move (the screenshots folder is outside the project and stays
untouched):

```bash
cp ~/Pictures/screenshots/<capture>.png <assetsDir>/<topic>-NN-<slug>.png
```

If the main repo's `assets/` directory doesn't exist yet, creating it is a one-time
setup step — the permission prompt is intentional.

## Wire the README

Insert or replace the section. Image refs are relative to the README's own
directory. Show the resulting diff to the user; committing and pushing stay with
the user.
