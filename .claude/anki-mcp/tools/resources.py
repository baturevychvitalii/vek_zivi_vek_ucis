"""MCP resources — static reference data served alongside tools."""
import pathlib

from core import mcp

_ref = pathlib.Path(__file__).parent / "ref"


@mcp.resource(
    "anki://template-reference",
    name="template-reference",
    description=(
        "Anki card template syntax and CSS conventions. "
        "Read this before calling update_model_templates or update_model_styling."
    ),
    mime_type="text/markdown",
)
def template_reference() -> str:
    """Anki card template and CSS cheat sheet."""
    return (_ref / "template-reference.md").read_text()


@mcp.resource(
    "anki://add-notes",
    name="add-notes",
    description=(
        "Note dict schema, field conventions by model type, cloze syntax, "
        "media references, and return value semantics. "
        "Read this before calling add_notes."
    ),
    mime_type="text/markdown",
)
def add_notes_reference() -> str:
    """add_notes input format and conventions."""
    return (_ref / "add-notes.md").read_text()
