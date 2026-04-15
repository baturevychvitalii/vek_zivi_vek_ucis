# CLAUDE.md

Personal flashcard system for language learning. Currently two decks — Spanish and English — with more potentially added later. Format is Anki-compatible pipe-separated text, but not locked in.

This project also serves as a sandbox for learning Claude Code and automating workflows. Some solutions may be intentionally overengineered for the sake of exploration.

## Big Picture

The long-term goal is a fully automated pipeline: capture phrases on a phone → generate cards → inject directly into Anki (via AnkiConnect), no manual steps. The skills and structure here are the foundation for that.

## Navigation

| Where | What |
|---|---|
| `decks/spanish/context.md` | Spanish deck — config, generation rules, files |
| `decks/english/context.md` | English deck — config, generation rules, files |
| `/anki-pipeline-add-cards` | Add cards (sync → backup → generate) |
| `.claude/meta/security.md` | Skill authoring rules — read before creating or modifying skills |
| `.claude/pipelines/` | Pipeline definitions |

When working in a deck, read its `context.md` first.

When creating or modifying a skill, read `.claude/meta/security.md` first.

When the user's intent is ambiguous — unclear whether to invoke an atomic skill or a pipeline — default to the pipeline. Pipelines are the safer path. Only invoke an atomic skill directly if the user explicitly names it.

## Universal Card Format

```
Front | Back | tag1 tag2 tag3
```

- `<br>` for line breaks within a cell
- Cloze syntax: `{{c1::answer}}`, `{{c1::answer::hint}}`
- Multi-cloze: `{{c1::word1}} {{c2::word2}}`
- 3–6 tags per card
