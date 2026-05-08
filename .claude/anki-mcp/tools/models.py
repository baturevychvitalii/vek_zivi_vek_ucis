"""Note type (model) introspection."""
from core import mcp, _call


@mcp.tool()
def model_names() -> list[str]:
    """Return all note type (model) names in the collection."""
    return _call("modelNames")


@mcp.tool()
def model_field_names(model_name: str) -> list[str]:
    """Return the field names for a note type, in definition order."""
    return _call("modelFieldNames", modelName=model_name)


@mcp.tool()
def model_templates(model_name: str) -> dict:
    """Return card template definitions (Front/Back HTML) for a note type."""
    return _call("modelTemplates", modelName=model_name)


@mcp.tool()
def model_styling(model_name: str) -> dict:
    """Return CSS styling for a note type."""
    return _call("modelStyling", modelName=model_name)
