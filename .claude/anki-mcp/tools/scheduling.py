"""Card scheduling — suspend, forget, relearn, answer, and interval queries."""
from core import mcp, _call, _log


@mcp.tool()
def are_suspended(card_ids: list[int]) -> list:
    """Return suspension state per card. True/false per ID; null for unknown cards."""
    return _call("areSuspended", cards=card_ids)


@mcp.tool()
def are_due(card_ids: list[int]) -> list[bool]:
    """Return whether each card is currently due for review."""
    return _call("areDue", cards=card_ids)


@mcp.tool()
def get_intervals(card_ids: list[int], complete: bool = False) -> list:
    """
    Return current interval (days) for each card.

    If complete=True, returns full interval history per card as nested lists.
    Negative values indicate cards in the learning phase (stored as seconds).
    """
    return _call("getIntervals", cards=card_ids, complete=complete)


@mcp.tool()
def suspend_cards(card_ids: list[int]) -> bool:
    """Suspend cards so they are excluded from review. Returns true on success."""
    _log(f"suspend_cards: {len(card_ids)} cards")
    return _call("suspend", cards=card_ids)


@mcp.tool()
def unsuspend_cards(card_ids: list[int]) -> bool:
    """Restore suspended cards to the review queue. Returns true on success."""
    _log(f"unsuspend_cards: {len(card_ids)} cards")
    return _call("unsuspend", cards=card_ids)


@mcp.tool()
def forget_cards(card_ids: list[int]) -> None:
    """Reset scheduling for cards — they become new again."""
    _log(f"forget_cards: {len(card_ids)} cards")
    _call("forgetCards", cards=card_ids)


@mcp.tool()
def relearn_cards(card_ids: list[int]) -> None:
    """Move cards back to the learning queue (as if answered 'Again')."""
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
    _log(f"answer_cards: {len(answers)} answers")
    return _call("answerCards", answers=answers)
