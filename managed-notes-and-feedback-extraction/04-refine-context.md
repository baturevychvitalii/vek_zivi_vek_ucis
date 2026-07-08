# 04 — Refine-context skill

*Depends on: 02 (extractor); 03 useful. New file:
`.claude/skills/anki-refine-context/SKILL.md` (builder mode).*

## Goal

A standalone command that turns the *feedback that was applied* into durable improvements to the
deck's generation guidelines — so the same class of error stops appearing. Closes the loop.

Usage: `/anki-refine-context <compiled context file path>`

## Design

1. **Load inputs** — the deck's `.compiled.md` + the feedback/edit records (from the extractor
   JSON persisted next to it, or from the `log` entries of the just-processed run — decide with
   03).
2. **Assess (quality crux — conservative):** distinguish *one-off factual corrections* (no
   guideline change) from *systemic patterns* (a recurring/generalizable gap the generator
   lacked). Under-propose rather than over-propose; over-proposing pollutes the context files.
3. **Generate chunks** — each = `{target section heading, proposed text, rationale citing the
   feedback it prevents}`. **Prefer additive, self-contained guidance over rewording existing
   lines** — additions attribute reliably in reverse-propagate; rewordings of merged lines risk
   mis-landing in the wrong source layer.
4. **Per-chunk approval** — present numbered; user approves a subset.
5. **Apply approved chunks to `.compiled.md`** (`Write(**/*.compiled.md)` is whitelisted).
6. **`/context-compiler:reverse-propagate <compiled path>`** — handles source attribution, the
   shared-layer confirmation guard, `.bak` backup, verbatim apply, deterministic verification.
7. **Report** — chunks applied/skipped + reverse-propagate result.

Runs in the **main context** (small context, interactive approval) — no fork worker needed.

## Verification (novel composition — verify end-to-end on Spanish)

Auto-applying chunks then reverse-propagating is new (reverse-propagate was built for human
hand-edits). Confirm: approved chunk lands in the correct **context-local** source
(`rioplatense-anki.md` / `focus_area.md`); `preprocess.py` shows it in fresh output; a fresh
`compile-context` reproduces it.

## Done when

- `/anki-refine-context` produces conservative, additive chunks; per-chunk approval works; approved
  text round-trips into source and survives recompile.

## Open questions

- Input source: persisted extractor JSON vs `log` entries (ties to 03).
- Should refine also run (gated) inside `pipe:anki-process-flags`, or stay standalone only?
  (Currently: standalone.)
