import os
import subprocess
from datetime import datetime
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent / "mem-bank.log"


def make_logger(tag):
    def log(detail):
        try:
            LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(LOG_PATH, "a") as f:
                f.write(f"{datetime.now().isoformat()}\t[{tag}]\t{detail}\n")
        except Exception:
            pass
    return log


def call_claude(prompt, model, recursion_guard=False):
    env = os.environ.copy()
    if recursion_guard:
        env["MEM_BANK_HOOK_RECURSION_GUARD"] = "1"
    result = subprocess.run(
        ["claude", "-p", "--model", model, prompt],
        capture_output=True, text=True, timeout=300, env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude exited {result.returncode}: {result.stderr.strip()}")
    return result.stdout.strip()
