#!/usr/bin/env python3
"""
Anki MCP server — thin MCP wrapper over AnkiConnect.

Exposes Anki operations as MCP tools so Claude can call them natively
without bash invocations or JSON string construction.

All logging goes to the project file logger (never stdout — stdout is the stdio transport).
"""
import json
import pathlib
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from utils.log import make_logger
from mcp.server.fastmcp import FastMCP
from launcher import ensure_anki_running

ANKI_CONNECT_URL = "http://localhost:8765"

_log = make_logger("server", pathlib.Path(__file__).resolve().parent / "anki-mcp.log")
mcp = FastMCP("anki")


def _call(action: str, **params) -> object:
    payload = {"action": action, "version": 6, "params": params}
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        ANKI_CONNECT_URL, data=data,
        headers={"Content-Type": "application/json"},
    )
    response = json.loads(urllib.request.urlopen(req, timeout=30).read())
    if response.get("error"):
        raise RuntimeError(response["error"])
    return response["result"]


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
    ensure_anki_running()
    _log(f"add_notes: {len(notes)} notes")
    return _call("addNotes", notes=notes)


@mcp.tool()
def sync() -> str:
    """
    Trigger an AnkiWeb sync via AnkiConnect.

    Fires and returns immediately — the sync runs in the background inside Anki.
    Returns a confirmation string; does not wait for sync completion.
    """
    ensure_anki_running()
    _log("sync triggered")
    _call("sync")
    return "sync triggered"


if __name__ == "__main__":
    _log("server starting")
    mcp.run()
