"""
Anki process lifecycle — start Anki if AnkiConnect is not reachable.

Designed for lazy invocation from tool handlers: call ensure_anki_running()
before any AnkiConnect request and it will block until Anki is up (or raise).
Safe to call from multiple MCP server instances: Anki's own single-instance
guard prevents duplicate processes, and the health-check is idempotent.
"""
import json
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

ANKI_CONNECT_URL = "http://localhost:8765"
_STARTUP_TIMEOUT_S = 30
_LOG_PATH = Path(__file__).resolve().parent / "anki-mcp.log"


def _log(detail: str) -> None:
    line = f"{datetime.now().isoformat()}\t[launcher]\t{detail}"
    print(line, file=sys.stderr)
    try:
        with open(_LOG_PATH, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def _is_anki_up() -> bool:
    try:
        payload = json.dumps({"action": "version", "version": 6}).encode()
        req = urllib.request.Request(
            ANKI_CONNECT_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=3)
        return True
    except Exception:
        return False


def ensure_anki_running() -> None:
    if _is_anki_up():
        return
    _log("AnkiConnect not reachable — launching Anki")
    subprocess.Popen(
        ["anki"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,  # detach from MCP server process group
    )
    for _ in range(_STARTUP_TIMEOUT_S):
        time.sleep(1)
        if _is_anki_up():
            _log("AnkiConnect ready")
            return
    raise RuntimeError(
        f"Anki launched but AnkiConnect did not become reachable within {_STARTUP_TIMEOUT_S}s"
    )
