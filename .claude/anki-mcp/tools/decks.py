"""Deck management — create, configure, move cards, export/import, sync."""
from core import mcp, _call, _log


@mcp.tool()
def deck_names() -> list[str]:
    """Return all deck names in the collection."""
    return _call("deckNames")


@mcp.tool()
def deck_stats(decks: list[str]) -> dict:
    """
    Return stats for named decks.

    Returns a dict keyed by deck ID. Each value has: deck_id, name,
    new_count, learn_count, review_count, total_in_deck.
    """
    return _call("getDeckStats", decks=decks)


@mcp.tool()
def get_decks(card_ids: list[int]) -> dict:
    """Return a mapping of deck name → [card IDs] for the given cards."""
    return _call("getDecks", cards=card_ids)


@mcp.tool()
def create_deck(deck: str) -> int:
    """Create a deck with the given name. Returns the new deck ID."""
    _log(f"create_deck: {deck!r}")
    return _call("createDeck", deck=deck)


@mcp.tool()
def get_deck_config(deck: str) -> dict:
    """Return the configuration object for the named deck."""
    return _call("getDeckConfig", deck=deck)


@mcp.tool()
def save_deck_config(config: dict) -> bool:
    """Save a deck configuration object (obtained via get_deck_config). Returns true on success."""
    _log(f"save_deck_config: id={config.get('id')}")
    return _call("saveDeckConfig", config=config)


@mcp.tool()
def change_deck(card_ids: list[int], deck: str) -> None:
    """Move cards to a different deck."""
    _log(f"change_deck: {len(card_ids)} cards → {deck!r}")
    _call("changeDeck", cards=card_ids, deck=deck)


@mcp.tool()
def delete_decks(decks: list[str], cards_too: bool = False) -> None:
    """
    Delete decks by name.

    Args:
      decks:     Deck names to delete.
      cards_too: If true, also delete all cards in those decks.
    """
    _log(f"delete_decks: {decks}, cards_too={cards_too}")
    _call("deleteDecks", decks=decks, cardsToo=cards_too)


@mcp.tool()
def export_deck(deck: str, path: str, include_sched: bool = True) -> bool:
    """
    Export an Anki deck to an .apkg file at the given absolute path.

    Args:
      deck:          Anki deck name as shown in Anki (e.g. "Español").
      path:          Absolute path for the output file, including filename and .apkg extension.
      include_sched: Include scheduling data (default true — preserves review history).

    Returns true on success. The target directory must already exist.
    """
    _log(f"export_deck: deck={deck!r}, path={path!r}, include_sched={include_sched}")
    return _call("exportPackage", deck=deck, path=path, includeSched=include_sched)


@mcp.tool()
def import_package(path: str) -> None:
    """Import an .apkg file at the given absolute path into Anki."""
    _log(f"import_package: path={path!r}")
    _call("importPackage", path=path)


@mcp.tool()
def sync() -> str:
    """
    Trigger an AnkiWeb sync via AnkiConnect.

    Fires and returns immediately — the sync runs in the background inside Anki.
    Returns a confirmation string; does not wait for sync completion.
    """
    _log("sync triggered")
    _call("sync")
    return "sync triggered"
