"""
Deck analytics — computed metrics derived from raw AnkiConnect data.

These tools answer questions about vocabulary size, learning rate, and
growth projections that AnkiConnect's raw API does not expose directly.
"""
import time

from core import mcp, _call, _log


@mcp.tool()
def vocabulary_snapshot(deck: str) -> dict:
    """
    Estimate vocabulary size and maturity breakdown for a deck.

    Classifies all cards by learning stage:
      - mature:   interval ≥ 21 days (solidly learned)
      - young:    interval 1–20 days (recently passed into review)
      - learning: currently in learning or relearning steps
      - new:      never studied

    The estimated_vocabulary is a weighted count (mature + 0.7 × young)
    that discounts words you've seen recently but may not yet retain.

    Args:
      deck: Anki deck name (e.g. "Español").

    Returns:
      total_notes, mature, young, learning, new, estimated_vocabulary,
      sample_mature (up to 10 front-field values from mature cards).
    """
    _log(f"vocabulary_snapshot: deck={deck!r}")
    card_ids = _call("findCards", query=f"deck:{deck}")
    if not card_ids:
        return {
            "total_notes": 0, "mature": 0, "young": 0,
            "learning": 0, "new": 0, "estimated_vocabulary": 0,
            "sample_mature": [],
        }

    cards = _call("cardsInfo", cards=card_ids)

    mature, young, learning, new_cards = [], [], [], []
    for c in cards:
        t, iv = c["type"], c["interval"]
        if t == 0:
            new_cards.append(c)
        elif t in (1, 3):
            learning.append(c)
        elif iv >= 21:
            mature.append(c)
        else:
            young.append(c)

    total_notes = len({c["note"] for c in cards})

    sample_mature: list[str] = []
    if mature:
        sample_note_ids = list({c["note"] for c in mature[:20]})[:10]
        sample_notes = _call("notesInfo", notes=sample_note_ids)
        for n in sample_notes:
            first_value = next(iter(n["fields"].values()))["value"]
            sample_mature.append(first_value)

    return {
        "total_notes": total_notes,
        "mature": len(mature),
        "young": len(young),
        "learning": len(learning),
        "new": len(new_cards),
        "estimated_vocabulary": len(mature) + int(0.7 * len(young)),
        "sample_mature": sample_mature,
    }


@mcp.tool()
def learning_velocity(deck: str, days: int = 90) -> dict:
    """
    Compute learning rate and vocabulary growth projections for a deck.

    Looks back over the given number of days to find how many new cards
    were introduced (first review of a previously-unseen card), then
    projects mature vocabulary at 30-day and 365-day horizons using a
    75% retention-to-mature assumption.

    Args:
      deck: Anki deck name (e.g. "Español").
      days: Lookback window in days (default 90).

    Returns:
      - days_analyzed
      - new_cards_introduced: unique new cards first reviewed in the window
      - new_cards_per_week: average rate over the window
      - current_mature: cards with interval ≥ 21 days right now
      - remaining_new: cards not yet studied
      - weeks_to_deck_completion: weeks at current rate to introduce all new cards
                                   (null if rate is 0 or no new cards remain)
      - projected_mature_30d: estimated mature count in 30 days
      - projected_mature_365d: estimated mature count in 365 days
    """
    _log(f"learning_velocity: deck={deck!r}, days={days}")

    now_ms = int(time.time() * 1000)
    cutoff_ms = now_ms - days * 86_400_000

    reviews = _call("cardReviews", deck=deck, startID=0)

    # First-ever review of a card: reviewType==0 (learning) AND previousInterval==0
    new_card_ids_in_window: set[int] = set()
    for r in reviews:
        review_time, card_id, _usn, _button, _new_iv, prev_iv, _factor, _dur, review_type = r
        if review_time >= cutoff_ms and review_type == 0 and prev_iv == 0:
            new_card_ids_in_window.add(card_id)

    new_per_week = len(new_card_ids_in_window) / (days / 7) if days > 0 else 0.0

    all_card_ids = _call("findCards", query=f"deck:{deck}")
    cards = _call("cardsInfo", cards=all_card_ids) if all_card_ids else []

    current_mature = sum(1 for c in cards if c["type"] == 2 and c["interval"] >= 21)
    remaining_new = sum(1 for c in cards if c["type"] == 0)

    weeks_to_complete = None
    if new_per_week > 0 and remaining_new > 0:
        weeks_to_complete = round(remaining_new / new_per_week, 1)

    retention = 0.75
    total = len(all_card_ids)
    projected_30 = min(current_mature + int(new_per_week * (30 / 7) * retention), total)
    projected_365 = min(current_mature + int(new_per_week * (365 / 7) * retention), total)

    return {
        "days_analyzed": days,
        "new_cards_introduced": len(new_card_ids_in_window),
        "new_cards_per_week": round(new_per_week, 1),
        "current_mature": current_mature,
        "remaining_new": remaining_new,
        "weeks_to_deck_completion": weeks_to_complete,
        "projected_mature_30d": projected_30,
        "projected_mature_365d": projected_365,
    }
