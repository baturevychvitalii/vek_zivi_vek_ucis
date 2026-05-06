import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HOOK_DIR = Path(__file__).resolve().parent
PROMPT_DUMP_PATH = HOOK_DIR / "last-prompt.txt"
TARGETS_DUMP_PATH = HOOK_DIR / "last-targets.txt"

sys.path.insert(0, str(HOOK_DIR))
from listener import read_transcript, extract_text, matched_any  # noqa: E402
from registry import load_banks, bank_effective_patterns, bank_small_bank_path  # noqa: E402
from utils import make_logger, call_claude as _call_claude  # noqa: E402

log = make_logger("small-bank")


def parse_args(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--subscriptions")
    p.add_argument("--worker", action="store_true",
                   help="internal: run as detached worker (reads prompt and targets from disk)")
    p.add_argument("--session-id", default="")
    return p.parse_args(argv)


def collect_user_prompts(events):
    prompts = []
    for ev in events:
        if ev.get("type") != "user":
            continue
        text = extract_text(ev.get("message", {}).get("content", "")).strip()
        if text:
            prompts.append(text)
    return prompts


def last_n_assistant_responses(events, n=3):
    out = []
    for ev in reversed(events):
        if ev.get("type") != "assistant":
            continue
        text = extract_text(ev.get("message", {}).get("content", "")).strip()
        if text:
            out.append(text)
            if len(out) >= n:
                break
    return list(reversed(out))


def git_status(cwd):
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=cwd, capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip()
    except Exception as e:
        return f"(git status failed: {e})"


RESPONSE_CAP = 3000

SYSTEM_REMINDER_RE = re.compile(
    r"<system-reminder\b[^>]*>.*?</system-reminder>",
    re.DOTALL | re.IGNORECASE,
)
COMMAND_NAME_RE = re.compile(
    r"<command-name>([^<]+)</command-name>",
    re.IGNORECASE,
)
TASK_NOTIFICATION_RE = re.compile(
    r"<task-notification\b[^>]*>.*?</task-notification>",
    re.DOTALL | re.IGNORECASE,
)
TASK_SUMMARY_RE = re.compile(
    r"<summary>([^<]+)</summary>",
    re.IGNORECASE,
)


def _format_task_notification(block):
    m = TASK_SUMMARY_RE.search(block)
    if m:
        return f"[task-notification: {m.group(1).strip()}]"
    return "[task-notification]"


def clean_user_prompt(text):
    m = COMMAND_NAME_RE.search(text)
    if m:
        return f"[invoked /{m.group(1).strip()}]"
    text = TASK_NOTIFICATION_RE.sub(lambda mm: _format_task_notification(mm.group(0)), text)
    return SYSTEM_REMINDER_RE.sub("", text).strip()


def slim_assistant(text):
    text = SYSTEM_REMINDER_RE.sub("", text).strip()
    if len(text) > RESPONSE_CAP:
        head = text[:1000]
        tail = text[-300:]
        elided = len(text) - len(head) - len(tail)
        text = f"{head}\n…[elided {elided} chars]…\n{tail}"
    return text


def build_prompt(prompts, last_responses, gstatus):
    cleaned_prompts = [clean_user_prompt(p) for p in prompts]
    cleaned_prompts = [p for p in cleaned_prompts if p]
    slim_responses = [slim_assistant(r) for r in last_responses]
    numbered = "\n".join(f"{i+1}. {p}" for i, p in enumerate(cleaned_prompts))
    total = len(slim_responses)
    rendered_responses = "\n\n".join(
        f"[{i+1}/{total}] {r}" for i, r in enumerate(slim_responses)
    )
    return (
        "You are summarizing a coding session for an append-only project memory file.\n\n"
        "STRICT RULES:\n"
        "- Do NOT open any files.\n"
        "- Do NOT use any tools.\n"
        "- Summarize only from the text provided below.\n"
        "- Output 2-4 plain prose sentences. No headings, no lists, no code fences.\n"
        "- Focus on what changed, what is still open, and where to resume.\n\n"
        f"--- USER PROMPTS ---\n{numbered}\n\n"
        f"--- LAST ASSISTANT RESPONSES (chronological, oldest first) ---\n{rendered_responses}\n\n"
        f"--- GIT STATUS ---\n{gstatus}\n"
    )


def call_claude(prompt):
    return _call_claude(prompt, "haiku")


def append_to_target(target, summary, session_id):
    target.parent.mkdir(parents=True, exist_ok=True)
    short_id = (session_id or "unknown")[:6]
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    block = f"## {stamp} (session {short_id})\n{summary}\n\n"
    with open(target, "a") as f:
        f.write(block)


def run_worker(session_id):
    log(f"worker started: pid={os.getpid()} session={session_id or 'unknown'}")
    try:
        prompt = PROMPT_DUMP_PATH.read_text()
    except Exception as e:
        log(f"worker failed to read prompt dump: {e}")
        return 1
    try:
        targets_text = TARGETS_DUMP_PATH.read_text()
        targets = [Path(t.strip()) for t in targets_text.splitlines() if t.strip()]
    except Exception as e:
        log(f"worker failed to read targets dump: {e}")
        return 1
    if not targets:
        log("worker: no targets in targets dump")
        return 0
    try:
        summary = call_claude(prompt)
    except Exception as e:
        log(f"worker claude call failed: {e}")
        return 1
    if not summary:
        log("worker: claude -p returned empty output")
        return 0
    log(f"worker claude response ({len(summary)} chars): {summary!r}")
    for target in targets:
        try:
            append_to_target(target, summary, session_id)
            log(f"worker appended summary to {target}")
        except Exception as e:
            log(f"worker append failed for {target}: {e}")
    return 0


def spawn_worker(session_id):
    cmd = [
        sys.executable, str(Path(__file__).resolve()),
        "--worker",
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

    if not args.subscriptions:
        log("hook mode requires --subscriptions")
        return 0

    log(
        f"called: subscriptions={args.subscriptions!r} "
        f"transcript={transcript_path} session={session_id} cwd={cwd}"
    )

    try:
        banks = load_banks(args.subscriptions, cwd)
    except Exception as e:
        log(f"failed to load subscriptions: {e}")
        return 0

    try:
        events = read_transcript(transcript_path)
    except Exception as e:
        log(f"failed to read transcript: {e}")
        return 0

    matched_targets = []
    for bank in banks:
        name = bank.get("name", "?")
        pattern_strs = bank_effective_patterns(bank)
        try:
            patterns = [re.compile(s) for s in pattern_strs]
        except re.error as e:
            log(f"bad pattern for bank {name!r}: {e}")
            continue
        if matched_any(events, patterns):
            target = bank_small_bank_path(bank, cwd)
            matched_targets.append(str(target))
            log(f"bank matched: {name!r} -> {target}")

    if not matched_targets:
        log("no bank matched in transcript — skipping")
        return 0

    try:
        prompts = collect_user_prompts(events)
        last_responses = last_n_assistant_responses(events, n=3)
        gstatus = git_status(cwd)
        pre_slim_chars = sum(len(p) for p in prompts) + sum(len(r) for r in last_responses)
        full_prompt = build_prompt(prompts, last_responses, gstatus)
        PROMPT_DUMP_PATH.write_text(full_prompt)
        TARGETS_DUMP_PATH.write_text("\n".join(matched_targets))
        log(
            f"prompt written ({len(full_prompt)} chars; pre-slim {pre_slim_chars}); "
            f"targets: {matched_targets}"
        )
        spawn_worker(session_id)
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
        return run_worker(args.session_id)

    return run_hook(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
