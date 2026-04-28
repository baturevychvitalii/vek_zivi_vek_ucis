import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HOOK_DIR = Path(__file__).resolve().parent
LOG_PATH = HOOK_DIR / "mem-bank.log"
PROMPT_DUMP_PATH = HOOK_DIR / "last-prompt.txt"


def log(detail):
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "a") as f:
            f.write(f"{datetime.now().isoformat()}\t[append-session-summary]\t{detail}\n")
    except Exception:
        pass


def parse_args(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--keywords")
    p.add_argument("--target")
    p.add_argument("--worker", action="store_true",
                   help="internal: run as detached worker (reads prompt from disk)")
    p.add_argument("--session-id", default="")
    return p.parse_args(argv)


def read_transcript(path):
    events = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def extract_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "\n".join(parts)
    return ""


def detect(events, patterns):
    for ev in events:
        if ev.get("type") == "user":
            text = extract_text(ev.get("message", {}).get("content", ""))
            for pat in patterns:
                if pat.search(text):
                    return True
        if ev.get("type") == "assistant":
            content = ev.get("message", {}).get("content", [])
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        tool_input = block.get("input", {}) or {}
                        for key in ("file_path", "path", "pattern"):
                            val = tool_input.get(key, "")
                            if isinstance(val, str):
                                for pat in patterns:
                                    if pat.search(val):
                                        return True
    return False


def collect_user_prompts(events):
    prompts = []
    for ev in events:
        if ev.get("type") != "user":
            continue
        text = extract_text(ev.get("message", {}).get("content", "")).strip()
        if text:
            prompts.append(text)
    return prompts


def last_assistant_response(events):
    for ev in reversed(events):
        if ev.get("type") != "assistant":
            continue
        text = extract_text(ev.get("message", {}).get("content", "")).strip()
        if text:
            return text
    return ""


def git_status(cwd):
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=cwd, capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip()
    except Exception as e:
        return f"(git status failed: {e})"


def build_prompt(prompts, last_asst, gstatus):
    numbered = "\n".join(f"{i+1}. {p}" for i, p in enumerate(prompts))
    return (
        "You are summarizing a coding session for an append-only project memory file.\n\n"
        "STRICT RULES:\n"
        "- Do NOT open any files.\n"
        "- Do NOT use any tools.\n"
        "- Summarize only from the text provided below.\n"
        "- Output 2-4 plain prose sentences. No headings, no lists, no code fences.\n"
        "- Focus on what changed, what is still open, and where to resume.\n\n"
        f"--- USER PROMPTS ---\n{numbered}\n\n"
        f"--- LAST ASSISTANT RESPONSE ---\n{last_asst}\n\n"
        f"--- GIT STATUS ---\n{gstatus}\n"
    )


def call_claude(prompt):
    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True, text=True, timeout=300,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude -p exited {result.returncode}: {result.stderr.strip()}")
    return result.stdout.strip()


def append_to_target(target, summary, session_id):
    target.parent.mkdir(parents=True, exist_ok=True)
    short_id = (session_id or "unknown")[:6]
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    block = f"## {stamp} (session {short_id})\n{summary}\n\n"
    with open(target, "a") as f:
        f.write(block)


def run_worker(target, session_id):
    log(f"worker started: pid={os.getpid()} target={target} session={session_id or 'unknown'}")
    try:
        prompt = PROMPT_DUMP_PATH.read_text()
    except Exception as e:
        log(f"worker failed to read prompt dump: {e}")
        return 1
    try:
        summary = call_claude(prompt)
    except Exception as e:
        log(f"worker claude call failed: {e}")
        return 1
    if not summary:
        log("worker: claude -p returned empty output")
        return 0
    log(f"worker claude response ({len(summary)} chars): {summary!r}")
    try:
        append_to_target(target, summary, session_id)
        log(f"worker appended summary to {target}")
    except Exception as e:
        log(f"worker append failed: {e}")
        return 1
    return 0


def spawn_worker(target, session_id):
    cmd = [
        sys.executable, str(Path(__file__).resolve()),
        "--worker",
        "--target", str(target),
        "--session-id", session_id,
    ]
    devnull_r = open(os.devnull, "rb")
    devnull_w = open(os.devnull, "ab")
    env = os.environ.copy()
    env["MEM_BANK_HOOK_RECURSION_GUARD"] = "1"
    proc = subprocess.Popen(
        cmd,
        stdin=devnull_r,
        stdout=devnull_w,
        stderr=devnull_w,
        start_new_session=True,
        close_fds=True,
        env=env,
    )
    log(f"detached worker spawned pid={proc.pid}")


def run_hook(args):
    try:
        raw = sys.stdin.read()
        inp = json.loads(raw) if raw.strip() else {}
    except Exception as e:
        log(f"failed to parse stdin: {e}")
        return 0

    if os.environ.get("MEM_BANK_HOOK_RECURSION_GUARD") == "1":
        log("recursion guard tripped (called from child claude -p) — skipping")
        return 0

    transcript_path = inp.get("transcript_path")
    session_id = inp.get("session_id", "")
    cwd = inp.get("cwd") or os.getcwd()

    if not transcript_path or not os.path.exists(transcript_path):
        log(f"missing transcript_path: {transcript_path}")
        return 0

    if not args.keywords or not args.target:
        log("hook mode requires --keywords and --target")
        return 0

    try:
        patterns = [re.compile(p.strip()) for p in args.keywords.split(",") if p.strip()]
    except re.error as e:
        log(f"bad regex in --keywords: {e}")
        return 0

    target = Path(args.target)
    if not target.is_absolute():
        target = Path(cwd) / target

    log(
        f"called: keywords={args.keywords!r} target={target} "
        f"transcript={transcript_path} session={session_id} cwd={cwd}"
    )

    try:
        events = read_transcript(transcript_path)
    except Exception as e:
        log(f"failed to read transcript: {e}")
        return 0

    if not detect(events, patterns):
        log("no keyword match in transcript — skipping")
        return 0

    try:
        prompts = collect_user_prompts(events)
        last_asst = last_assistant_response(events)
        gstatus = git_status(cwd)
        full_prompt = build_prompt(prompts, last_asst, gstatus)
        PROMPT_DUMP_PATH.write_text(full_prompt)
        log(f"claude input written to {PROMPT_DUMP_PATH} ({len(full_prompt)} chars)")
        spawn_worker(target, session_id)
    except Exception as e:
        log(f"hook failed before spawn: {e}")
        return 0

    return 0


def main(argv):
    try:
        args = parse_args(argv)
    except SystemExit:
        log("argparse failed")
        return 0

    if args.worker:
        if not args.target:
            log("worker mode requires --target")
            return 1
        return run_worker(Path(args.target), args.session_id)

    return run_hook(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
