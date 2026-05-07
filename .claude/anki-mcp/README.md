# Anki MCP Subsystem

Self-contained MCP server that exposes Anki operations as native Claude tools. Claude calls tools directly instead of constructing JSON strings and invoking bash.

The subsystem is consolidated under `.claude/anki-mcp/`. Outside that folder, two host-fixed locations carry thin handles that point in: `.mcp.json` (server registration) and `.gitignore` (runtime artifacts if any are added later).

## Subsystem files (this folder)

| Path | What |
|---|---|
| `./server.py` | The MCP server. Exposes `add_notes` and `sync` as tools. All Anki calls route through AnkiConnect at `localhost:8765`. |

## Tools

### Query

| Tool | What |
|---|---|
| `find_cards(query)` | Search cards by raw Anki query string (e.g. `"deck:Español tag:food"`). Returns list of card IDs. |
| `find_flagged_cards(flag, deck?)` | Find cards by flag name (`red`, `green`, `purple`, …), optionally scoped to a deck. |
| `cards_info(card_ids)` | Fetch full metadata for a list of card IDs — fields, tags, flags, scheduling data. |
| `notes_info(note_ids)` | Fetch full metadata for a list of note IDs — fields, tags, associated card IDs. |

### Write

| Tool | What |
|---|---|
| `add_notes(notes)` | Add notes to Anki. Each note: `{deckName, modelName, fields, tags}`. Returns list of note IDs; null = duplicate skipped. |
| `update_note_fields(note_id, fields)` | Update specific fields on an existing note in-place. Omitted fields are untouched. |
| `set_card_flag(card_id, flag)` | Set a card's flag by name: `none`, `red`, `orange`, `green`, `blue`, `pink`, `turquoise`, `purple`. |
| `delete_notes(note_ids)` | Permanently delete notes and all their associated cards. Irreversible. |

### Collection

| Tool | What |
|---|---|
| `export_deck(deck, path, include_sched)` | Export a deck to an `.apkg` file at the given absolute path. `include_sched=true` preserves review history. |
| `sync()` | Trigger AnkiWeb sync. Fires and returns immediately. |

When invoked by Claude, tools are namespaced as `mcp__anki__<tool_name>`.

## Host-fixed handles (point into the subsystem)

| Path | What it does |
|---|---|
| `.mcp.json` | Registers the server with Claude Code as a project-scoped stdio MCP server. |

## Setup

**Create the venv and install the MCP SDK (one-time):**
```
python3 -m venv .claude/anki-mcp/.venv
.claude/anki-mcp/.venv/bin/pip install mcp
```

The venv is gitignored — run these commands after cloning or on a fresh machine.

**Register with Claude Code (already done via `.mcp.json` — no action needed).**

**Restart Claude Code** after any changes to `.mcp.json` or `server.py` — the server is spawned at startup, not on demand.

## Stdio discipline

This server uses stdio transport. Stdout is the protocol channel — anything written to stdout that isn't routed through the MCP SDK corrupts the JSON-RPC stream silently. Rules:
- Never `print()` outside the SDK
- All debug/log output goes to `stderr`

## Growing the server

Add a new tool by decorating a function with `@mcp.tool()` in `server.py`. The docstring becomes the tool description Claude reads — write it as a precise, self-contained spec. Restart Claude Code after adding tools.

AnkiConnect action reference: https://foosoft.net/projects/anki-connect/
