"""
Shared state for the Anki MCP server.

Provides: mcp instance, _call() (with Anki startup folded in), FLAGS, _log.
Imported by every tools/* module — nothing here may import from tools/.
"""
import functools
import json
import pathlib
import urllib.request

from mcp.server.fastmcp import FastMCP
from utils.log import make_logger
from launcher import ensure_anki_running

ANKI_CONNECT_URL = "http://localhost:8765"

FLAGS = {
    "none": 0, "red": 1, "orange": 2, "green": 3,
    "blue": 4, "pink": 5, "turquoise": 6, "purple": 7,
}

_log_path = pathlib.Path(__file__).resolve().parent / "anki-mcp.log"
_log = make_logger("server", _log_path)
_call_log = make_logger("call", _log_path)

mcp = FastMCP("anki")

_original_tool = mcp.tool

def _logging_tool(*args, **kwargs):
    register = _original_tool(*args, **kwargs)
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*a, **kw):
            _call_log(fn.__name__)
            return fn(*a, **kw)
        return register(wrapper)
    return decorator

mcp.tool = _logging_tool


def _call(action: str, **params) -> object:
    ensure_anki_running()
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
