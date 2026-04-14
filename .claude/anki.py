#!/usr/bin/env python3
"""
Thin AnkiConnect HTTP client for Claude skills.

Usage:
  python3 .claude/anki.py '<json_payload>'   # JSON string as argument
  python3 .claude/anki.py <filepath>         # read JSON payload from file
  python3 .claude/anki.py                    # read JSON payload from stdin

Payload format: {"action": "...", "params": {...}}
Output: raw JSON result printed to stdout.
"""
import json, sys, urllib.request

def call_anki(payload):
    if "version" not in payload:
        payload["version"] = 6
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        "http://localhost:8765", data=data,
        headers={"Content-Type": "application/json"}
    )
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg.startswith("{"):
            payload = json.loads(arg)
        else:
            with open(arg) as f:
                payload = json.load(f)
    else:
        payload = json.load(sys.stdin)

    result = call_anki(payload)
    print(json.dumps(result, ensure_ascii=False))
