#!/usr/bin/env python3
"""
Anki MCP server — entry point.

Sets up the import path, imports core (mcp instance + _call),
then imports the tools package which triggers @mcp.tool() registration
across all submodules.

All logging goes to the project file logger (never stdout — stdout is the stdio transport).
"""
import pathlib
import sys

_here = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_here))           # anki-mcp/ → core, launcher, tools
sys.path.insert(0, str(_here.parent))    # .claude/   → utils

from core import mcp, _log
import tools  # noqa: F401 — import triggers @mcp.tool() registration in all submodules

if __name__ == "__main__":
    _log("server starting")
    mcp.run()
