"""Tag operations — all tag mutations are note-level in Anki."""
from core import mcp, _call, _log


@mcp.tool()
def get_tags() -> list[str]:
    """Return all tags used in the collection."""
    return _call("getTags")


@mcp.tool()
def add_tags(note_ids: list[int], tags: str) -> None:
    """Add space-separated tags to notes. Existing tags are preserved."""
    _log(f"add_tags: {len(note_ids)} notes, tags={tags!r}")
    _call("addTags", notes=note_ids, tags=tags)


@mcp.tool()
def remove_tags(note_ids: list[int], tags: str) -> None:
    """Remove space-separated tags from notes."""
    _log(f"remove_tags: {len(note_ids)} notes, tags={tags!r}")
    _call("removeTags", notes=note_ids, tags=tags)


@mcp.tool()
def update_note_tags(note_id: int, tags: list[str]) -> None:
    """Replace all tags on a note. Destructive — omitted tags are removed."""
    _log(f"update_note_tags: note_id={note_id}, tags={tags}")
    _call("updateNoteTags", note=note_id, tags=tags)


@mcp.tool()
def clear_unused_tags() -> None:
    """Remove tags from the tag list that are not used by any note."""
    _log("clear_unused_tags")
    _call("clearUnusedTags")


@mcp.tool()
def replace_tags_in_all_notes(old_tag: str, new_tag: str) -> None:
    """Rename a tag across every note in the collection."""
    _log(f"replace_tags_in_all_notes: {old_tag!r} → {new_tag!r}")
    _call("replaceTagsInAllNotes", tag_to_replace=old_tag, replace_with_tag=new_tag)
