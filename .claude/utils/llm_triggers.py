import os
import subprocess


def call_isolated(prompt, model, recursion_guard=False):
    """Spawn a fresh `claude -p` subprocess with no session context."""
    env = os.environ.copy()
    if recursion_guard:
        env["HOOK_RECURSION_GUARD"] = "1"
    result = subprocess.run(
        ["claude", "-p", "--model", model, prompt],
        capture_output=True, text=True, timeout=300, env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude exited {result.returncode}: {result.stderr.strip()}")
    return result.stdout.strip()
