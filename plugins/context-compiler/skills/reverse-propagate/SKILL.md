---
name: reverse-propagate
description: Back-propagate manual edits made in a compiled.md down to its source layer files
disable-model-invocation: false
context: fork
---

Propagate hand-edits made directly in a `*.compiled.md` back into the source layer
files that compile into it. This is the **inverse** of `/context-compiler:compile`.

Use when the user edited a compiled document by hand and wants those exact edits to live
in the real sources, so a future compile reproduces them.

**This is a lossy inverse.** Compilation reorders, groups, and merges layers, so a line in
the compiled file does not map mechanically to one source line. Your job is to land each
hand-edit **verbatim** in the **one** source file it belongs to — the rules below exist to
pick that file correctly and to keep shared layers (which other decks depend on) safe.

Usage: `/context-compiler:reverse-propagate <path-to-file.compiled.md>`

e.g. `/context-compiler:reverse-propagate decks/languages/spanish/rioplatense-anki.compiled.md`

## Validate Input and Resolve the Source Entry

The argument must end with `.compiled.md`. If it does not, report the error and stop.

Derive the **source entry file** by stripping the suffix: `<stem>.compiled.md` → `<stem>.md`
(same directory). e.g. `rioplatense-anki.compiled.md` → `rioplatense-anki.md`.

If the entry file does not exist, report "Source entry not found: <entry>" and stop.

The **deck directory** is the entry file's parent directory. Remember it — it is how you
tell deck-local layers from shared layers later.

## Back Up the Edited Compiled File

The user's hand-edited compiled file is the source of truth for this run, and a later
compile will overwrite it. Preserve it first:
```bash
cp <file.compiled.md> <file.compiled.md>.bak
```
Do this before touching anything else, so the edits can never be lost mid-run.

## Enumerate Source Layers

Run:
```bash
python3 plugins/context-compiler/include_graph.py <entry>
```

This prints the entry file followed by every transitive `#include` dependency, one path
per line. These are the only candidate targets for every edit.

Classify each listed file:
- **Deck-local** — path is under the deck directory. Safe to edit freely.
- **Shared** — path is outside the deck directory (e.g. `decks/languages/language-defaults.md`,
  `decks/deck-defaults.md`, `decks/languages/cloze-deletion.md`). These compile into **other
  decks too** — editing them changes rules for every deck. Treat as protected (see the
  Shared-layer guard).

## Establish the Edit Set

Generate the current source-truth deterministically:
```bash
python3 plugins/context-compiler/preprocess.py <entry>
```
This is the flat concatenation of every layer as the sources stand now. Read it and read
the edited `*.compiled.md`.

Compare them to recover the genuine hand-edits, and **only** those:
- Content in the compiled file but absent from the source-truth → an **addition** or, if it
  is a reworded version of an existing line, a **modification**.
- Content in the source-truth but absent from the compiled file → a **removal**.
- Pure reordering, regrouping under a shared heading, and the dedup/merge collapsing that
  compilation legitimately performs are **not edits** — never propagate them.

Produce an explicit edit list: for each edit, record `{kind: add | modify | remove, the
exact edited text, the surrounding section/heading}`.

## Attribute Each Edit to a Source File

For every edit, decide which single source file owns it:

- **Default to the most specific (entry) deck-local file.** Genuinely new, deck-specific
  content goes to the entry file — or to a deck-local include like `focus_area.md` when it
  plainly belongs to that file's topic (e.g. a dialect rule → the dialect file).
- **To modify or remove existing text**, find the source file whose text matches the
  *pre-edit* content (use the source-truth as the bridge). That file owns the line.
- **Shared-layer guard.** If the owner is a **shared** file, do not auto-apply. A hand-edit
  can reword an upstream line using a deck-specific concept (e.g. elaborating a shared
  "Is cloze improving retention?" bullet with "…or duplicating the *production card*?" —
  "production card" is a Spanish-layer notion). For each such edit, use AskUserQuestion to
  confirm: write into the shared file (changes all decks) **or** override it deck-locally in
  the entry file. Default to the deck-local override. Never silently write a shared layer.

## Apply the Edits Verbatim

Land the user's **exact edited text** in the owning file — do not reword it to match the
layer's style. The compiled wording is what the user chose; reproduce it character-for-character.
- **add** → insert the exact text under the matching heading in the target file.
- **modify** → replace the owning file's old line with the user's exact new text.
- **remove** → delete the line.

Deck-local edits: apply directly. Shared-layer edits: apply only the resolution the user
confirmed.

## Verify Deterministically

Re-run the preprocessor:
```bash
python3 plugins/context-compiler/preprocess.py <entry>
```
Confirm each propagated edit's exact text now appears in the fresh preprocessed output (and
each removal is gone). This deterministically proves the content landed in a source file —
unlike re-running the LLM compile, which is nondeterministic. Report any edit that did not
land.

## Report

```
✓ Propagated <N> edit(s) from <file.compiled.md>  (backup: <file.compiled.md>.bak)

  <edit summary> → <target source file>
  ...

Shared-layer: <confirmed resolutions, or "none">
Verified: all edits present in fresh preprocessed output
```
List any edits that could not be attributed or did not verify, and stop for the user.
