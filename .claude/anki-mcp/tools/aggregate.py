"""
Higher-level aggregation tools.

These collapse multi-step AnkiConnect roundtrips into single calls,
returning structures ready for AI consumption (fields flattened, objects merged).
"""
from core import mcp, _call, _log, FLAGS


@mcp.tool()
def get_all_notes(deck: str, include_scheduling: bool = False) -> list[dict]:
    """
    Return all notes in a deck with fields flattened to {name: value}.

    Collapses find_notes() + notes_info() into one call and removes the
    {value, order} nesting that raw notes_info() returns. Each note becomes
    a clean dict ready for AI consumption or bulk operations.

    Args:
      deck:               Anki deck name (e.g. "Español").
      include_scheduling: If true, merges interval, ease_factor, lapses, and due
                          per card into each note. Costs an extra cards_info() call.

    Each returned dict:
      - note_id (int), model_name (str), tags (list[str])
      - fields (dict): {field_name: value} — flattened, no {value, order} wrapper
      - If include_scheduling: intervals, ease_factors, lapses, due (lists, one per card)
    """
    _log(f"get_all_notes: deck={deck!r}, include_scheduling={include_scheduling}")
    note_ids = _call("findNotes", query=f"deck:{deck}")
    if not note_ids:
        return []

    notes_raw = _call("notesInfo", notes=note_ids)
    result = [
        {
            "note_id": n["noteId"],
            "model_name": n["modelName"],
            "tags": n["tags"],
            "fields": {k: v["value"] for k, v in n["fields"].items()},
        }
        for n in notes_raw
    ]

    if include_scheduling:
        all_card_ids = [cid for n in notes_raw for cid in n["cards"]]
        cards_raw = _call("cardsInfo", cards=all_card_ids)
        cards_by_note: dict[int, list[dict]] = {}
        for c in cards_raw:
            cards_by_note.setdefault(c["note"], []).append(c)
        for entry, n in zip(result, notes_raw):
            cards = cards_by_note.get(n["noteId"], [])
            entry["intervals"] = [c["interval"] for c in cards]
            entry["ease_factors"] = [c["factor"] for c in cards]
            entry["lapses"] = [c["lapses"] for c in cards]
            entry["due"] = [c["due"] for c in cards]

    return result


@mcp.tool()
def get_flagged_notes(deck: str, flag: str) -> list[dict]:
    """
    Return flagged notes in a deck, merged and ready for editing.

    Collapses find_flagged_cards() → cards_info() → notes_info() into one call.
    Returns flattened field dicts (no {value, order} nesting) plus the card_id
    needed for set_card_flag().

    Args:
      deck: Anki deck name (e.g. "Español").
      flag: Flag name — one of: none, red, orange, green, blue, pink, turquoise, purple.

    Each returned dict:
      - card_id (int): pass to set_card_flag() to change the flag
      - note_id (int): pass to update_note_fields() / update_note()
      - model_name (str): note type (e.g. "Basic", "Cloze")
      - deck_name (str): deck the card belongs to
      - tags (list[str])
      - fields (dict): {field_name: value} — flattened
    """
    if flag not in FLAGS:
        raise ValueError(f"Unknown flag {flag!r}. Valid values: {', '.join(FLAGS)}")
    _log(f"get_flagged_notes: deck={deck!r}, flag={flag!r}")

    card_ids = _call("findCards", query=f"deck:{deck} flag:{FLAGS[flag]}")
    if not card_ids:
        return []

    cards_raw = _call("cardsInfo", cards=card_ids)
    note_ids = list({c["note"] for c in cards_raw})
    notes_raw = _call("notesInfo", notes=note_ids)
    notes_by_id = {n["noteId"]: n for n in notes_raw}

    return [
        {
            "card_id": c["cardId"],
            "note_id": c["note"],
            "model_name": c["modelName"],
            "deck_name": c["deckName"],
            "tags": notes_by_id[c["note"]]["tags"],
            "fields": {
                k: v["value"]
                for k, v in notes_by_id[c["note"]]["fields"].items()
            },
        }
        for c in cards_raw
    ]
