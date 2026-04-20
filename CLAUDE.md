# CLAUDE.md

Personal flashcard system for learning languages and other domains. Currently three decks — Spanish, English, and Instruments — with more potentially added later. Cards are generated and pushed directly to Anki via AnkiConnect; `.apkg` snapshots serve as the durable archive.

This project also serves as a sandbox for learning Claude Code and automating workflows. Some solutions may be intentionally overengineered for the sake of exploration.

## Navigation

| Where | What |
|---|---|
| `decks/languages/spanish/inheritable-spanish.md` | Spanish deck — dialect, card types, domain tags |
| `decks/languages/english/inheritable-english.md` | English deck — card types, domain tags |
| `decks/instruments/inheritable-instruments.md` | Instruments deck — visual identification, image handling, IPA |
| `/pipe:anki-add-cards` | Add cards  |
| `/pipe:anki-process-flags` | Process flags / perform regular deck maintenence / cleanup |
| `.claude/meta/builder/context.md` | Builder mode — read before creating or modifying skills/pipelines |
| `.claude/meta/architect/context.md` | Architect mode — read before any structural or design decisions |


When creating, modifying, or deleting any file under `.claude/commands/` or `.claude/pipeline-specifications/`, read `.claude/meta/builder/context.md` first.

When the user's intent is ambiguous — unclear whether to invoke an atomic skill or a pipeline — default to the pipeline. Pipelines are the safer path. Only invoke an atomic skill directly if the user explicitly names it.

