# Managed Notes & Feedback Extraction

Big-picture initiative doc. Read this first each session; then open the subtask file you're
tackling. Keep this file the source of truth for **locked decisions** so future sessions don't
relitigate them.

---

## The problem

- Red-flag corrections fix one card but discard *why* it was wrong.
- The `[...]`-in-a-field convention is LLM-fragile and collides with real content.
- Extraction that should be **deterministic** is currently done by an LLM.
- Guideline gaps that caused the error are never fed back into card generation, so the same
  class of mistake recurs.

## The shift

1. **Deterministic extraction, LLM judgment.** Cards get a dedicated `user_feedback` field.
   A deterministic anki-mcp tool extracts feedback → JSON. The LLM only does what it's good at:
   applying the edit and proposing guideline improvements.
2. **Close the loop.** After edits are applied, propose improvements to the deck's *compiled
   context* so the same error is prevented at generation time — landed in source layers via the
   existing `context-compiler:reverse-propagate`.

## Smart-MCP boundary

anki-mcp gains awareness of **managed note types** — models carrying `user_feedback` + `log`
fields. It owns the *mechanism*; the project owns the *policy*.

| Concern | Owner |
|---|---|
| Field contract (`user_feedback`, `log`), ensure-fields, extraction, flag-setting | **anki-mcp** |
| *Which* note types are managed | **project** (injected into anki-mcp, never hardcoded) |

anki-mcp is a standalone public submodule — keeping policy out preserves its reusability.

## Field contract

- **`user_feedback`** — user-written input. Non-empty = "process me". Cleared after processing.
- **`log`** — append-only history (creation source, edit transitions). Hidden: not referenced in
  card templates, so it never renders on a card.

## Lifecycle (target state)

```
user types feedback in `user_feedback`
   → extractor tool: sets RED flag (visual convenience only) + emits JSON
   → red-edit: LLM applies edit → clear `user_feedback`, append `log`, flip flag GREEN
   → refine: LLM proposes compiled-context chunks → user approves subset
   → apply chunks to .compiled.md → reverse-propagate to source layers
```

## Locked decisions

| # | Decision |
|---|---|
| D1 | Trigger is **`user_feedback` non-empty**, not the flag. |
| D2 | The extractor **sets the RED flag itself**, purely for visual convenience in Anki's browser. |
| D3 | The extractor is an **MCP tool in the anki-mcp repo** (deterministic Python), reused by red-edit and refine. |
| D4 | anki-mcp is **"smart"**: aware of `user_feedback` + `log` fields = managed models. |
| D5 | **Mechanism in anki-mcp; the managed-model set is project policy**, injected (config/param), never hardcoded in anki-mcp. |
| D6 | Two fields, two lifecycles: `user_feedback` (input, cleared) and `log` (append-only history). |
| D7 | Refine still writes to `.compiled.md` then runs `reverse-propagate` — unchanged from earlier plan. |
| D8 | Adding fields to existing note types is acceptable; new users need a **bootstrap** step ("MCP ensures your note types have the managed fields"). |

## Subtasks

| File | Subtask | Depends on |
|---|---|---|
| `01-managed-fields-foundation.md` | Field contract + `ensure_managed_fields` + project config for the managed set + onboarding | — |
| `02-feedback-extractor.md` | Deterministic anki-mcp extraction tool → JSON + auto RED flag | 01 |
| `03-red-edit-rework.md` | red-edit consumes JSON; clears feedback, appends log, flips flag | 02 |
| `04-refine-context.md` | New `anki-refine-context` skill: chunks → `.compiled.md` → reverse-propagate | 02 (03 useful) |
| `05-card-log.md` | The `log` field: append-only history, retrospection/rollback (was "Task B") | 01 |

## Sequencing

```
01 ──► 02 ──► 03
        └───► 04
01 ──────────► 05
```

Start with **01** (foundation) — everything depends on the field contract and the managed-model
config. Then **02** (extractor) unblocks both 03 and 04. **05** can proceed after 01 independently.

## Cross-cutting notes

- **Submodule workflow:** anki-mcp is a separate repo/submodule. Any change there follows the
  established flow: commit upstream in anki-mcp → bump the monorepo's `anki-mcp` pointer.
- **Existing anki-mcp primitives** to build on: `add_model_field`, `model_field_names`,
  `update_note_fields`, `set_card_flag`, `find_notes`, `notes_info`, `get_flagged_notes`.
