# CLAUDE.md

Personal flashcard system for language learning. Currently two decks — Spanish and English — with more potentially added later. Cards are generated and pushed directly to Anki via AnkiConnect; `.apkg` snapshots serve as the durable archive.

This project also serves as a sandbox for learning Claude Code and automating workflows. Some solutions may be intentionally overengineered for the sake of exploration.

## Navigation

| Where | What |
|---|---|
| `decks/context.md` | Shared deck defaults — models, cloze syntax, tagging, card design |
| `decks/spanish/context.md` | Spanish deck — dialect, card types, domain tags |
| `decks/english/context.md` | English deck — card types, domain tags |
| `/pipe:anki-add-cards` | Add cards (sync → backup → generate) |
| `.claude/meta/builder/context.md` | Builder mode — read before creating or modifying skills/pipelines |
| `.claude/meta/architect/context.md` | Architect mode — read before any structural or design decisions |

When working in a deck, read its `context.md` first.

When creating, modifying, or deleting any file under `.claude/commands/` or `.claude/pipeline-specifications/`, read `.claude/meta/builder/context.md` first.

When the user's intent is ambiguous — unclear whether to invoke an atomic skill or a pipeline — default to the pipeline. Pipelines are the safer path. Only invoke an atomic skill directly if the user explicitly names it.

## Card Generation Format

Cards are generated and displayed in this format during the add-cards workflow before conversion to AnkiConnect payloads:

```
Front | Back | tag1 tag2 tag3
```

- `<br>` for line breaks within a cell
- Cloze syntax: `{{c1::answer}}`, `{{c1::answer::hint}}`
- Multi-cloze: `{{c1::word1}} {{c2::word2}}`
- 3–6 tags per card
