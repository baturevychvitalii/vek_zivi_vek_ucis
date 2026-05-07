#!/usr/bin/env python3
"""
Anki MCP server — thin MCP wrapper over AnkiConnect.

Exposes Anki operations as MCP tools so Claude can call them natively
without bash invocations or JSON string construction.

All logging goes to the project file logger (never stdout — stdout is the stdio transport).
"""
import json
import pathlib
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from utils.log import make_logger
from mcp.server.fastmcp import FastMCP
from launcher import ensure_anki_running

ANKI_CONNECT_URL = "http://localhost:8765"

FLAGS = {
    "none": 0, "red": 1, "orange": 2, "green": 3,
    "blue": 4, "pink": 5, "turquoise": 6, "purple": 7,
}

_log = make_logger("server", pathlib.Path(__file__).resolve().parent / "anki-mcp.log")
mcp = FastMCP("anki")


def _call(action: str, **params) -> object:
    payload = {"action": action, "version": 6, "params": params}
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        ANKI_CONNECT_URL, data=data,
        headers={"Content-Type": "application/json"},
    )
    response = json.loads(urllib.request.urlopen(req, timeout=30).read())
    if response.get("error"):
        raise RuntimeError(response["error"])
    return response["result"]


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
    ensure_anki_running()
    _log(f"find_cards: query={query!r}")
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
    ensure_anki_running()
    _log(f"find_flagged_cards: flag={flag!r}, deck={deck!r}")
    return _call("findCards", query=query)


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
    ensure_anki_running()
    _log(f"cards_info: {len(card_ids)} cards")
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
    ensure_anki_running()
    _log(f"notes_info: {len(note_ids)} notes")
    return _call("notesInfo", notes=note_ids)


@mcp.tool()
def delete_notes(note_ids: list[int]) -> None:
    """
    Permanently delete notes and all their associated cards from Anki.

    This is irreversible. Each note maps to one or more cards — all are removed.
    Confirm with the user before calling.

    Typical pipeline:
      find_cards(query) → cards_info() → extract note IDs → delete_notes()
    """
    ensure_anki_running()
    _log(f"delete_notes: {len(note_ids)} notes")
    _call("deleteNotes", notes=note_ids)


@mcp.tool()
def update_note_fields(note_id: int, fields: dict) -> None:
    """
    Update one or more fields on an existing note in-place.

    Supply only the fields you want to change — omitted fields are untouched.

    Examples:
      Basic card:  fields={"Front": "new question", "Back": "new answer"}
      Cloze card:  fields={"Text": "{{c1::new cloze}}", "Back Extra": "hint"}

    Field names must match the note's model exactly (case-sensitive).
    """
    ensure_anki_running()
    _log(f"update_note_fields: note_id={note_id}, fields={list(fields)}")
    _call("updateNoteFields", note={"id": note_id, "fields": fields})


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
    ensure_anki_running()
    _log(f"set_card_flag: card_id={card_id}, flag={flag!r}")
    _call("setSpecificValueOfCard", card=card_id, keys=["flags"], newValues=[FLAGS[flag]])


@mcp.tool()
def export_deck(deck: str, path: str, include_sched: bool = True) -> bool:
    """
    Export an Anki deck to an .apkg file at the given absolute path.

    Args:
      deck:         Anki deck name as shown in Anki (e.g. "Español").
      path:         Absolute path for the output file, including filename and .apkg extension.
      include_sched: Include scheduling data (default true — preserves review history).

    Returns true on success. The target directory must already exist.
    The caller is responsible for path construction (date-stamping, collision avoidance, etc.).
    """
    ensure_anki_running()
    _log(f"export_deck: deck={deck!r}, path={path!r}, include_sched={include_sched}")
    return _call("exportPackage", deck=deck, path=path, includeSched=include_sched)


@mcp.tool()
def add_notes(notes: list[dict]) -> list:
    """
    Add notes to Anki via AnkiConnect.

    Each note must be a dict with:
      - deckName (str): target deck, e.g. "Spanish"
      - modelName (str): note type, e.g. "Cloze" or "Basic"
      - fields (dict): field-name → value mapping
      - tags (list[str]): tag list, may be empty

    Returns a list of note IDs in the same order as input.
    Null at a position means the note was a duplicate and was skipped.
    """
    ensure_anki_running()
    _log(f"add_notes: {len(notes)} notes")
    return _call("addNotes", notes=notes)


@mcp.tool()
def sync() -> str:
    """
    Trigger an AnkiWeb sync via AnkiConnect.

    Fires and returns immediately — the sync runs in the background inside Anki.
    Returns a confirmation string; does not wait for sync completion.
    """
    ensure_anki_running()
    _log("sync triggered")
    _call("sync")
    return "sync triggered"


if __name__ == "__main__":
    _log("server starting")
    mcp.run()
