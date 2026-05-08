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


# ── Card search ────────────────────────────────────────────────────────────────

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
def find_notes(query: str) -> list[int]:
    """Search for notes matching an Anki query string. Returns note IDs."""
    ensure_anki_running()
    _log(f"find_notes: query={query!r}")
    return _call("findNotes", query=query)


# ── Card / note info ───────────────────────────────────────────────────────────

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
def cards_to_notes(card_ids: list[int]) -> list[int]:
    """Convert card IDs to their corresponding note IDs."""
    ensure_anki_running()
    return _call("cardsToNotes", cards=card_ids)


# ── Note mutations ─────────────────────────────────────────────────────────────

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
def can_add_notes(notes: list[dict]) -> list[bool]:
    """Check whether notes can be added (duplicate detection). Same format as add_notes()."""
    ensure_anki_running()
    return _call("canAddNotes", notes=notes)


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
def update_note(note_id: int, fields: dict = None, tags: list[str] = None) -> None:
    """
    Atomically update fields and/or tags on a note.

    Prefer this over update_note_fields when changing both fields and tags in one step.
    At least one of fields or tags must be provided.
    """
    ensure_anki_running()
    note: dict = {"id": note_id}
    if fields is not None:
        note["fields"] = fields
    if tags is not None:
        note["tags"] = tags
    if len(note) == 1:
        raise ValueError("At least one of fields or tags must be provided")
    _log(f"update_note: note_id={note_id}, fields={list(fields or {})}, tags={tags}")
    _call("updateNote", note=note)


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
def remove_empty_notes() -> None:
    """Remove notes with no cards (e.g. after template deletion). Irreversible."""
    ensure_anki_running()
    _log("remove_empty_notes")
    _call("removeEmptyNotes")


# ── Tags ───────────────────────────────────────────────────────────────────────

@mcp.tool()
def get_tags() -> list[str]:
    """Return all tags used in the collection."""
    ensure_anki_running()
    return _call("getTags")


@mcp.tool()
def add_tags(note_ids: list[int], tags: str) -> None:
    """Add space-separated tags to notes. Existing tags are preserved."""
    ensure_anki_running()
    _log(f"add_tags: {len(note_ids)} notes, tags={tags!r}")
    _call("addTags", notes=note_ids, tags=tags)


@mcp.tool()
def remove_tags(note_ids: list[int], tags: str) -> None:
    """Remove space-separated tags from notes."""
    ensure_anki_running()
    _log(f"remove_tags: {len(note_ids)} notes, tags={tags!r}")
    _call("removeTags", notes=note_ids, tags=tags)


@mcp.tool()
def update_note_tags(note_id: int, tags: list[str]) -> None:
    """Replace all tags on a note. Destructive — omitted tags are removed."""
    ensure_anki_running()
    _log(f"update_note_tags: note_id={note_id}, tags={tags}")
    _call("updateNoteTags", note=note_id, tags=tags)


@mcp.tool()
def clear_unused_tags() -> None:
    """Remove tags from the tag list that are not used by any note."""
    ensure_anki_running()
    _log("clear_unused_tags")
    _call("clearUnusedTags")


@mcp.tool()
def replace_tags_in_all_notes(old_tag: str, new_tag: str) -> None:
    """Rename a tag across every note in the collection."""
    ensure_anki_running()
    _log(f"replace_tags_in_all_notes: {old_tag!r} → {new_tag!r}")
    _call("replaceTagsInAllNotes", tag_to_replace=old_tag, replace_with_tag=new_tag)


# ── Flags ──────────────────────────────────────────────────────────────────────

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


# ── Decks ──────────────────────────────────────────────────────────────────────

@mcp.tool()
def deck_names() -> list[str]:
    """Return all deck names in the collection."""
    ensure_anki_running()
    return _call("deckNames")


@mcp.tool()
def deck_stats(decks: list[str]) -> dict:
    """
    Return stats for named decks.

    Returns a dict keyed by deck ID. Each value has: deck_id, name,
    new_count, learn_count, review_count, total_in_deck.
    """
    ensure_anki_running()
    return _call("getDeckStats", decks=decks)


@mcp.tool()
def get_decks(card_ids: list[int]) -> dict:
    """Return a mapping of deck name → [card IDs] for the given cards."""
    ensure_anki_running()
    return _call("getDecks", cards=card_ids)


@mcp.tool()
def create_deck(deck: str) -> int:
    """Create a deck with the given name. Returns the new deck ID."""
    ensure_anki_running()
    _log(f"create_deck: {deck!r}")
    return _call("createDeck", deck=deck)


@mcp.tool()
def get_deck_config(deck: str) -> dict:
    """Return the configuration object for the named deck."""
    ensure_anki_running()
    return _call("getDeckConfig", deck=deck)


@mcp.tool()
def save_deck_config(config: dict) -> bool:
    """Save a deck configuration object (obtained via get_deck_config). Returns true on success."""
    ensure_anki_running()
    _log(f"save_deck_config: id={config.get('id')}")
    return _call("saveDeckConfig", config=config)


@mcp.tool()
def change_deck(card_ids: list[int], deck: str) -> None:
    """Move cards to a different deck."""
    ensure_anki_running()
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
    ensure_anki_running()
    _log(f"delete_decks: {decks}, cards_too={cards_too}")
    _call("deleteDecks", decks=decks, cardsToo=cards_too)


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
def import_package(path: str) -> None:
    """Import an .apkg file at the given absolute path into Anki."""
    ensure_anki_running()
    _log(f"import_package: path={path!r}")
    _call("importPackage", path=path)


# ── Card scheduling ────────────────────────────────────────────────────────────

@mcp.tool()
def are_suspended(card_ids: list[int]) -> list:
    """Return suspension state per card. True/false per ID; null for unknown cards."""
    ensure_anki_running()
    return _call("areSuspended", cards=card_ids)


@mcp.tool()
def are_due(card_ids: list[int]) -> list[bool]:
    """Return whether each card is currently due for review."""
    ensure_anki_running()
    return _call("areDue", cards=card_ids)


@mcp.tool()
def get_intervals(card_ids: list[int], complete: bool = False) -> list:
    """
    Return current interval (days) for each card.

    If complete=True, returns full interval history per card as nested lists.
    Negative values indicate cards in the learning phase (stored as seconds).
    """
    ensure_anki_running()
    return _call("getIntervals", cards=card_ids, complete=complete)


@mcp.tool()
def suspend_cards(card_ids: list[int]) -> bool:
    """Suspend cards so they are excluded from review. Returns true on success."""
    ensure_anki_running()
    _log(f"suspend_cards: {len(card_ids)} cards")
    return _call("suspend", cards=card_ids)


@mcp.tool()
def unsuspend_cards(card_ids: list[int]) -> bool:
    """Restore suspended cards to the review queue. Returns true on success."""
    ensure_anki_running()
    _log(f"unsuspend_cards: {len(card_ids)} cards")
    return _call("unsuspend", cards=card_ids)


@mcp.tool()
def forget_cards(card_ids: list[int]) -> None:
    """Reset scheduling for cards — they become new again."""
    ensure_anki_running()
    _log(f"forget_cards: {len(card_ids)} cards")
    _call("forgetCards", cards=card_ids)


@mcp.tool()
def relearn_cards(card_ids: list[int]) -> None:
    """Move cards back to the learning queue (as if answered 'Again')."""
    ensure_anki_running()
    _log(f"relearn_cards: {len(card_ids)} cards")
    _call("relearnCards", cards=card_ids)


@mcp.tool()
def answer_cards(answers: list[dict]) -> list[bool]:
    """
    Simulate answering cards in a review session.

    Each answer: {"cardId": int, "ease": int}
    Ease values: 1=Again, 2=Hard, 3=Good, 4=Easy.
    Returns true per card if the answer was applied successfully.
    """
    ensure_anki_running()
    _log(f"answer_cards: {len(answers)} answers")
    return _call("answerCards", answers=answers)


# ── Model introspection ────────────────────────────────────────────────────────

@mcp.tool()
def model_names() -> list[str]:
    """Return all note type (model) names in the collection."""
    ensure_anki_running()
    return _call("modelNames")


@mcp.tool()
def model_field_names(model_name: str) -> list[str]:
    """Return the field names for a note type, in definition order."""
    ensure_anki_running()
    return _call("modelFieldNames", modelName=model_name)


@mcp.tool()
def model_templates(model_name: str) -> dict:
    """Return card template definitions (Front/Back HTML) for a note type."""
    ensure_anki_running()
    return _call("modelTemplates", modelName=model_name)


@mcp.tool()
def model_styling(model_name: str) -> dict:
    """Return CSS styling for a note type."""
    ensure_anki_running()
    return _call("modelStyling", modelName=model_name)


# ── Media ──────────────────────────────────────────────────────────────────────

@mcp.tool()
def store_media_file(filename: str, data: str = None, path: str = None) -> str:
    """
    Store a file in Anki's media collection.

    Args:
      filename: Target filename (e.g. "my-image.jpg").
      data:     Base64-encoded file content.
      path:     Absolute path to the source file on disk.
    Exactly one of data or path must be provided. Returns the stored filename.
    """
    ensure_anki_running()
    _log(f"store_media_file: {filename!r}")
    if data is not None:
        return _call("storeMediaFile", filename=filename, data=data)
    elif path is not None:
        return _call("storeMediaFile", filename=filename, path=path)
    raise ValueError("Either data or path must be provided")


@mcp.tool()
def retrieve_media_file(filename: str) -> str:
    """Retrieve a media file from Anki as a base64-encoded string."""
    ensure_anki_running()
    return _call("retrieveMediaFile", filename=filename)


@mcp.tool()
def get_media_files_names(pattern: str = "*") -> list[str]:
    """List media filenames matching a glob pattern (default: all files)."""
    ensure_anki_running()
    return _call("getMediaFilesNames", pattern=pattern)


@mcp.tool()
def get_media_dir_path() -> str:
    """Return the absolute path to Anki's media directory."""
    ensure_anki_running()
    return _call("getMediaDirPath")


@mcp.tool()
def delete_media_file(filename: str) -> None:
    """Permanently delete a file from Anki's media collection."""
    ensure_anki_running()
    _log(f"delete_media_file: {filename!r}")
    _call("deleteMediaFile", filename=filename)


# ── Statistics ─────────────────────────────────────────────────────────────────

@mcp.tool()
def get_collection_stats() -> str:
    """Return collection-wide statistics as an HTML string."""
    ensure_anki_running()
    return _call("getCollectionStatsHTML", wholeCollection=True)


@mcp.tool()
def card_reviews(deck: str, start_id: int = 0) -> list[list]:
    """
    Return review log entries for a deck since start_id.

    Each entry: [reviewTime, cardId, usn, buttonPressed, newInterval,
                 previousInterval, newFactor, reviewDuration, reviewType].
    Use get_latest_review_id() to get start_id for incremental fetches.
    """
    ensure_anki_running()
    return _call("cardReviews", deck=deck, startID=start_id)


@mcp.tool()
def get_reviews_of_cards(card_ids: list[int]) -> dict:
    """Return complete review history per card ID as a dict of lists."""
    ensure_anki_running()
    return _call("getReviewsOfCards", cards=card_ids)


@mcp.tool()
def get_latest_review_id(deck: str) -> int:
    """Return the ID of the most recent review log entry in a deck."""
    ensure_anki_running()
    return _call("getLatestReviewID", deck=deck)


# ── Sync ───────────────────────────────────────────────────────────────────────

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
