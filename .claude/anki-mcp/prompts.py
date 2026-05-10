"""MCP prompt definitions for the Anki server."""
from core import mcp, _log
from mcp.server.fastmcp.prompts.base import UserMessage
from tools.analytics import vocabulary_snapshot, learning_velocity
from tools.aggregate import get_flagged_notes

_ACTIONABLE_FLAGS = ("red", "orange", "purple", "blue", "pink", "turquoise")


@mcp.prompt()
def deck_briefing(deck: str) -> UserMessage:
    """Snapshot of a deck's current state — vocabulary, progress, and pending flags."""
    _log(f"deck_briefing: deck={deck!r}")

    snap = vocabulary_snapshot(deck)
    vel = learning_velocity(deck)

    flagged_sections: list[str] = []
    for flag in _ACTIONABLE_FLAGS:
        notes = get_flagged_notes(deck, flag)
        if not notes:
            continue
        snippets = [next(iter(n["fields"].values()), "—") for n in notes[:5]]
        more = f" (+{len(notes) - 5} more)" if len(notes) > 5 else ""
        lines = "\n".join(f"  - {s}" for s in snippets)
        flagged_sections.append(f"{flag.upper()} ({len(notes)}){more}:\n{lines}")

    flags_block = "\n\n".join(flagged_sections) if flagged_sections else "None."

    completion_line = (
        f"  - Deck completion: ~{vel['weeks_to_deck_completion']}w at current rate\n"
        if vel["weeks_to_deck_completion"]
        else ""
    )

    text = (
        f"## Deck briefing: {deck}\n\n"
        f"### Vocabulary\n"
        f"  - Total notes: {snap['total_notes']}\n"
        f"  - Mature (>=21d): {snap['mature']}\n"
        f"  - Young (1-20d): {snap['young']}\n"
        f"  - Learning: {snap['learning']}\n"
        f"  - New (unseen): {snap['new']}\n"
        f"  - Estimated vocabulary: {snap['estimated_vocabulary']}\n\n"
        f"### Learning velocity ({vel['days_analyzed']}d window)\n"
        f"  - New cards introduced: {vel['new_cards_introduced']}\n"
        f"  - Rate: {vel['new_cards_per_week']:.1f} cards/week\n"
        f"  - Projected mature in 30d: {vel['projected_mature_30d']}\n"
        f"  - Projected mature in 365d: {vel['projected_mature_365d']}\n"
        f"{completion_line}"
        f"\n### Flags pending attention\n"
        f"{flags_block}\n"
    )

    return UserMessage(text)
