# CLAUDE.md

Personal flashcard system for learning languages and other domains. Currently three decks — Spanish, English, and Instruments — with more potentially added later. Cards are generated and pushed directly to Anki via AnkiConnect; `.apkg` snapshots serve as the durable archive.

The longer-term direction is a generalized **learning conductor** — an interface for learning skills seamlessly, where each area carries its own intake, encoding, execution, and observability. Flashcards remain one capability among several. 

## Navigation

| Where | What |
|---|---|
| `decks/languages/spanish/inheritable-spanish.md` | Spanish deck — dialect, card types, domain tags |
| `decks/languages/spanish/resources.md` | Spanish lit-search — source registry, search URLs, author coverage |
| `decks/languages/spanish/reading-log/context.md` | Spanish reading history — past books, difficulty verdicts |
| `decks/languages/english/inheritable-english.md` | English deck — card types, domain tags |
| `decks/instruments/inheritable-instruments.md` | Instruments deck — visual identification, image handling, IPA |
| `/pipe:anki-add-cards` | Add cards  |
| `/pipe:anki-process-flags` | Process flags / perform regular deck maintenence / cleanup |
| `.claude/meta/builder/context.md` | Builder mode — read before creating or modifying skills/pipelines |
| `.claude/meta/architect/context.md` | Architect mode — read before any structural or design decisions |


When the user's intent is ambiguous — unclear whether to invoke an atomic skill or a pipeline — default to the pipeline. Pipelines are the safer path.

