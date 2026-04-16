# Deck Defaults

Shared rules inherited by all decks. Deck-specific `context.md` files override or extend these.

## Models

```
basicModel: "Basic"
```

## Card Generation Rules (shared)

### Input Rules
- One card input per line break — multiple sentences on one line = one input
- Generate as many cards as the input warrants; never fewer than implied; no filler cards

### Card Design Rules
- One learning objective per card
- No redundant paraphrase cards

### Tagging (shared)

Always include `cardtype::*`. 3–6 tags total. Additional mandatory tags may be defined per deck or domain.

```
cardtype::<type>     (mandatory — types defined per deck)
```

### Output Format

Cards are previewed before conversion to AnkiConnect payloads:

```
Front | Back | tag1 tag2 tag3
```

- `<br>` for line breaks within a cell

## Directory Structure

Each deck directory contains:
- `context.md` — deck rules and config (this file pattern)
- `backups/` — `.apkg` snapshots (content git-ignored; directory tracked via `.gitkeep`)

Skills derive the backup path from the location of `context.md`: `BACKUP_DIR = dirname(context.md) + /backups`. No path is hardcoded in skill specs.
