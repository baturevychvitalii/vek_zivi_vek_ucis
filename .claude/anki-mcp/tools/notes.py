"""Note creation, mutation, and deletion."""
from core import mcp, _call, _log


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
    _log(f"add_notes: {len(notes)} notes")
    return _call("addNotes", notes=notes)


@mcp.tool()
def can_add_notes(notes: list[dict]) -> list[bool]:
    """Check whether notes can be added (duplicate detection). Same format as add_notes()."""
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
    _log(f"update_note_fields: note_id={note_id}, fields={list(fields)}")
    _call("updateNoteFields", note={"id": note_id, "fields": fields})


@mcp.tool()
def update_note(note_id: int, fields: dict = None, tags: list[str] = None) -> None:
    """
    Atomically update fields and/or tags on a note.

    Prefer this over update_note_fields when changing both fields and tags in one step.
    At least one of fields or tags must be provided.
    """
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
    _log(f"delete_notes: {len(note_ids)} notes")
    _call("deleteNotes", notes=note_ids)


@mcp.tool()
def remove_empty_notes() -> None:
    """Remove notes with no cards (e.g. after template deletion). Irreversible."""
    _log("remove_empty_notes")
    _call("removeEmptyNotes")
