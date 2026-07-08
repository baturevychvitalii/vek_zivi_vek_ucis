# 03 — red-edit rework

*Depends on: 02 (extractor). File: `.claude/skills/anki-process-red-edit/SKILL.md` (builder mode).*

## Goal

Rework `anki-process-red-edit` to consume the extractor's JSON instead of LLM-parsing `[...]`,
apply the edit (LLM judgment), then update managed fields and the flag.

## Design

Replace current Steps 1–2 (find flagged + parse brackets) with:
1. Call the **extractor tool** (02) → JSON of cards with non-empty `user_feedback`.
2. **Apply edits** — LLM interprets each card's `user_feedback` and edits the relevant fields
   (this is the retained `edit-card` judgment step; feedback is now card-level, LLM decides which
   fields to touch).
3. **User confirmation** — as today.
4. **On apply, per card:**
   - `update_note_fields` with the changed fields;
   - **clear `user_feedback`** (processed);
   - **append to `log`** an edit entry (`edited <ts> | <feedback> | <field>: before→after`);
   - flip flag RED → **GREEN** (`set_card_flag`).
5. **Report** — as today.

Naming: the skill name/trigger language shifts from "RED-flagged" to "cards with feedback"; the
flag becomes a *view* set by the extractor, not the trigger (D1/D2). Consider renaming the skill
later; not required for this subtask.

## Done when

- red-edit no longer parses `[...]`; it reads the extractor JSON.
- After a run: edited fields updated, `user_feedback` cleared, `log` appended, flag GREEN.
- The old bracket-stripping logic is gone; docs/usage updated.

## Open questions

- Does red-edit write `log` directly, or delegate to a shared "append log" helper (shared with 05
  / add-cards)? Prefer a shared write-path so log format stays consistent.
- Keep the separate `.edit-ledger.json` artifact for refine (04), or does refine re-run the
  extractor / read `log`? (If `log` captures the transition, refine may not need a separate
  ledger — decide with 04.)
