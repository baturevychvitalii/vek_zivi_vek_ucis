"""Anki media collection — store, retrieve, list, delete."""
from core import mcp, _call, _log


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
    _log(f"store_media_file: {filename!r}")
    if data is not None:
        return _call("storeMediaFile", filename=filename, data=data)
    if path is not None:
        return _call("storeMediaFile", filename=filename, path=path)
    raise ValueError("Either data or path must be provided")


@mcp.tool()
def retrieve_media_file(filename: str) -> str:
    """Retrieve a media file from Anki as a base64-encoded string."""
    return _call("retrieveMediaFile", filename=filename)


@mcp.tool()
def get_media_files_names(pattern: str = "*") -> list[str]:
    """List media filenames matching a glob pattern (default: all files)."""
    return _call("getMediaFilesNames", pattern=pattern)


@mcp.tool()
def get_media_dir_path() -> str:
    """Return the absolute path to Anki's media directory."""
    return _call("getMediaDirPath")


@mcp.tool()
def delete_media_file(filename: str) -> None:
    """Permanently delete a file from Anki's media collection."""
    _log(f"delete_media_file: {filename!r}")
    _call("deleteMediaFile", filename=filename)
