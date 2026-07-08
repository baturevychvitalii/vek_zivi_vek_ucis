# 01 — Managed-fields foundation ✓ DONE

*Depends on: nothing. Everything else depends on this.*

## Goal

Establish the "managed note type" concept: the `user_feedback` + `log` field contract, an
idempotent way to ensure a model has them, and where the project declares *which* models are
managed — with anki-mcp owning mechanism, the project owning policy (D5).

## Design

**Field contract** (anki-mcp constant): a managed model has fields `user_feedback` and `log`.
- `user_feedback` — input; non-empty triggers processing; cleared after.
- `log` — append-only; hidden (not in templates).

**`ensure_managed_fields` (new anki-mcp tool):** given a set of model names, for each model add
any missing managed field via the existing `add_model_field`. Idempotent — safe to run repeatedly
and on already-managed models. Returns what it added vs. what was already present. This is the
**bootstrap** a new user runs so their note types gain the fields (D8).

**Policy — which models are managed (project-owned):** anki-mcp must NOT hardcode
`Production`/`Cloze`. Options to decide here:
- (a) caller passes the model list to every tool call;
- (b) project keeps a small config (e.g. `groves/managed-models.json` or a field in an existing
  config) and the skills read it and pass it through;
- (c) convention (naming/tag).
- **Leaning (b):** a project config file listing managed models; skills load it and pass the list
  into anki-mcp tools. Keeps anki-mcp generic and the policy visible/versioned in the project.

**Template safety:** `log` (and `user_feedback`, if you don't want it shown) must not appear in
card templates → Anki won't render them. Confirm none of the managed models reference these
fields in their Front/Back templates after adding.

## What was built (actual implementation)

Rather than an explicit `ensure_managed_fields` MCP tool, the mechanism is a **lazy startup
bootstrap** in `anki-mcp/managed_note_types/bootstrap.py`:

- Fires once on the **first `_call()` to AnkiConnect** in a session (not at server startup) — so
  sessions that never touch Anki pay zero cost.
- Config path passed via `--managed-config groves/managed-models.json` in `.mcp.json` args.
- `groves/managed-models.json` declares each managed note type with its full domain field list
  (`is_cloze`, `fields`). Bootstrap creates missing note types and adds any missing managed fields.
- `MANAGED_FIELDS = ("user_feedback", "log")` lives in `bootstrap.py`.
- Templates are built from domain fields only — managed fields are hidden by default.

**Decisions locked here:**
- Config at `groves/managed-models.json` (option b from design).
- Cloze managed globally (option 2 from 05) — `user_feedback` + `log` added to the shared Cloze model.
- No `unmanage`/removal path — add-only for now.
