"""Collection-level statistics and review history."""
from core import mcp, _call


@mcp.tool()
def get_collection_stats() -> str:
    """Return collection-wide statistics as an HTML string."""
    return _call("getCollectionStatsHTML", wholeCollection=True)


@mcp.tool()
def card_reviews(deck: str, start_id: int = 0) -> list[list]:
    """
    Return review log entries for a deck since start_id.

    Each entry: [reviewTime, cardId, usn, buttonPressed, newInterval,
                 previousInterval, newFactor, reviewDuration, reviewType].

    reviewType values: 0=learning, 1=review, 2=relearn, 3=cram.
    buttonPressed: 1=Again, 2=Hard, 3=Good, 4=Easy.

    Use get_latest_review_id() to get start_id for incremental fetches.
    """
    return _call("cardReviews", deck=deck, startID=start_id)


@mcp.tool()
def get_reviews_of_cards(card_ids: list[int]) -> dict:
    """Return complete review history per card ID as a dict of lists."""
    return _call("getReviewsOfCards", cards=card_ids)


@mcp.tool()
def get_latest_review_id(deck: str) -> int:
    """Return the ID of the most recent review log entry in a deck."""
    return _call("getLatestReviewID", deck=deck)
