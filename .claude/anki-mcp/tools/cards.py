"""Card search, card metadata, and flag operations."""
from core import mcp, _call, _log, FLAGS


@mcp.tool()
def find_cards(query: str) -> list[int]:
    """
    Search for cards matching an AnkiConnect query string.

    Query syntax mirrors Anki's browser search:
      - "deck:Español"           cards in a specific deck
      - "tag:geography"          cards with a tag
      - "deck:Español tag:food"  combine with spaces (AND)

    For flag-based searches use find_flagged_cards() — it accepts
    human-readable flag names instead of numeric flag codes.

    Returns a list of card IDs. Empty list if no matches.
    """
    return _call("findCards", query=query)


@mcp.tool()
def find_flagged_cards(flag: str, deck: str = None) -> list[int]:
    """
    Find all cards carrying a named flag, optionally scoped to a deck.

    Args:
      flag: Flag name — one of: none, red, orange, green, blue, pink, turquoise, purple.
      deck: Anki deck name to scope the search (e.g. "Español"). Omit to search all decks.

    Returns a list of card IDs. Empty list if no matches.
    """
    if flag not in FLAGS:
        raise ValueError(f"Unknown flag {flag!r}. Valid values: {', '.join(FLAGS)}")
    query = f"flag:{FLAGS[flag]}"
    if deck:
        query = f"deck:{deck} {query}"
    return _call("findCards", query=query)


@mcp.tool()
def find_notes(query: str) -> list[int]:
    """Search for notes matching an Anki query string. Returns note IDs."""
    return _call("findNotes", query=query)


@mcp.tool()
def cards_info(card_ids: list[int]) -> list[dict]:
    """
    Fetch full metadata for a list of card IDs.

    Returns one dict per card with keys including:
      - cardId, note (int): card and note identifiers
      - deckName, modelName (str): deck and note type
      - fields (dict): field-name → {value, order} mapping
      - tags (list[str]): note tags
      - flags (int): flag value (0=none, 1=red, 2=orange, 3=green,
                     4=blue, 5=pink, 6=turquoise, 7=purple)
      - due, interval, factor, reps, lapses: scheduling data

    Pass the result of find_cards() directly as input.
    """
    return _call("cardsInfo", cards=card_ids)


@mcp.tool()
def notes_info(note_ids: list[int]) -> list[dict]:
    """
    Fetch full metadata for a list of note IDs.

    Returns one dict per note with keys:
      - noteId (int): note identifier
      - modelName (str): note type (e.g. "Basic", "Cloze")
      - fields (dict): field-name → {value, order} mapping
      - tags (list[str]): note tags
      - cards (list[int]): card IDs belonging to this note

    Note IDs appear as card["note"] in cards_info() output.
    Deduplicate before calling when deriving from a cards_info() result.
    """
    return _call("notesInfo", notes=note_ids)


@mcp.tool()
def cards_to_notes(card_ids: list[int]) -> list[int]:
    """Convert card IDs to their corresponding note IDs."""
    return _call("cardsToNotes", cards=card_ids)


@mcp.tool()
def set_card_flag(card_id: int, flag: str) -> None:
    """
    Set the flag on a card.

    Args:
      card_id: Card ID to update.
      flag:    Flag name — one of: none, red, orange, green, blue, pink, turquoise, purple.

    Common use: flip "red" → "green" after applying an edit instruction.
    """
    if flag not in FLAGS:
        raise ValueError(f"Unknown flag {flag!r}. Valid values: {', '.join(FLAGS)}")
    _log(f"set_card_flag: card_id={card_id}, flag={flag!r}")
    _call("setSpecificValueOfCard", card=card_id, keys=["flags"], newValues=[FLAGS[flag]])
