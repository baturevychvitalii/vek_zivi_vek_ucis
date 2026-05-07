import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_CLAUDE_DIR = _SCRIPT_DIR.parent

sys.path.insert(0, str(_SCRIPT_DIR))
sys.path.insert(0, str(_CLAUDE_DIR))
from registry import load_banks, bank_archive_dir, populated_banks  # noqa: E402
from utils.log import make_logger  # noqa: E402
from utils.llm_triggers import call_isolated as _call_claude  # noqa: E402

log = make_logger("big-bank", _SCRIPT_DIR / "mem-bank.log")

FILENAME_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*\.md$")
SESSION_HEADER_RE = re.compile(
    r"^## \d{4}-\d{2}-\d{2} \d{2}:\d{2} \(session ([a-zA-Z0-9]+)\)",
    re.MULTILINE,
)


def parse_args(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--subscriptions")
    p.add_argument("--source")
    p.add_argument("--archive-dir")
    p.add_argument("--backup-dir")
    p.add_argument("--branch", default="")
    return p.parse_args(argv)


def detect_branch(explicit):
    if explicit:
        return explicit
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            name = result.stdout.strip()
            if name:
                return name
    except Exception:
        pass
    return "unknown"


def extract_sessions(source_text):
    return SESSION_HEADER_RE.findall(source_text)


def build_prompt(source_text, branch, existing_filenames):
    listed = "\n".join(f"- {n}" for n in sorted(existing_filenames)) or "(none)"
    return (
        "You are summarizing a branch's project-development log into a durable archive entry.\n\n"
        "INPUT — small-bank.md from the branch:\n"
        "```\n"
        f"{source_text}\n"
        "```\n\n"
        f"BRANCH: {branch}\n\n"
        "EXISTING ARCHIVE FILENAMES (do not collide — pick a more specific name if your topic overlaps):\n"
        f"{listed}\n\n"
        "TASK — produce a single JSON object, no commentary, with exactly two keys:\n"
        '  "filename" — kebab-case .md filename describing the topic (e.g., "mem-bank-graduation.md").\n'
        "                Lowercase letters, digits, and hyphens only; ends with .md. Be specific enough\n"
        "                to differentiate from the existing filenames listed above.\n"
        '  "summary"  — 4–8 sentences of plain prose. Describe the procedure, the challenges,\n'
        "                and the WHYs of the decisions, drawn only from the input above. No headings,\n"
        "                no lists, no code fences.\n\n"
        "Output the JSON object and nothing else."
    )


def call_claude(prompt):
    return _call_claude(prompt, "sonnet", recursion_guard=True)


def parse_response(raw):
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if not m:
            raise ValueError(f"no JSON object found in response; raw={raw!r}")
        try:
            obj = json.loads(m.group(0))
        except json.JSONDecodeError as e:
            raise ValueError(f"claude response is not valid JSON: {e}; raw={raw!r}")
    if not isinstance(obj, dict):
        raise ValueError(f"claude response is not a JSON object; raw={raw!r}")
    filename = obj.get("filename")
    summary = obj.get("summary")
    if not isinstance(filename, str) or not isinstance(summary, str):
        raise ValueError(f"claude response missing string filename/summary; raw={raw!r}")
    if not FILENAME_RE.match(filename):
        raise ValueError(f"filename {filename!r} does not match kebab-case .md shape")
    return filename, summary.strip()


def resolve_collision(archive_dir, filename):
    target = archive_dir / filename
    if not target.exists():
        return target
    stem = filename[:-3]
    n = 2
    while True:
        candidate = archive_dir / f"{stem}-{n}.md"
        if not candidate.exists():
            return candidate
        n += 1


def topic_title_from_filename(filename):
    stem = filename[:-3] if filename.endswith(".md") else filename
    return " ".join(part.capitalize() for part in stem.split("-"))


def write_archive(target, title, branch, sessions, summary, archive_link):
    sessions_str = ", ".join(sessions) if sessions else "n/a"
    today = datetime.now().strftime("%Y-%m-%d")
    body = (
        f"# {title}\n\n"
        f"<{today} — branch {branch} — sessions {sessions_str}>\n\n"
        f"## Summary\n{summary}\n\n"
        f"## Archive\n[Small bank sessions]({archive_link})\n"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body)


def backup_source(source, backup_dir, stamp=None):
    backup_dir.mkdir(parents=True, exist_ok=True)
    if stamp is None:
        stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    dest = backup_dir / f"{stamp}-small-bank.md"
    shutil.copy2(source, dest)
    return dest


def graduate_one(source, archive_dir, backup_dir, branch, name=""):
    label = f"[{name}] " if name else ""
    log(f"{label}called: source={source} archive_dir={archive_dir} backup_dir={backup_dir} branch={branch!r}")

    if not source.exists():
        log(f"{label}source missing — clean no-op")
        print(f"{label}{source}: not found, nothing to graduate")
        return 0

    try:
        source_text = source.read_text()
    except Exception as e:
        log(f"{label}failed to read source: {e}")
        print(f"error: failed to read {source}: {e}", file=sys.stderr)
        return 1

    if not source_text.strip():
        log(f"{label}source empty — clean no-op")
        print(f"{label}{source}: empty, nothing to graduate")
        return 0

    sessions = extract_sessions(source_text)

    archive_dir.mkdir(parents=True, exist_ok=True)
    existing = [p.name for p in archive_dir.glob("*.md")]

    prompt = build_prompt(source_text, branch, existing)

    try:
        raw = call_claude(prompt)
    except Exception as e:
        log(f"{label}claude call failed: {e}")
        print(f"error: claude call failed: {e}", file=sys.stderr)
        return 1
    log(f"{label}claude response ({len(raw)} chars)")

    try:
        filename, summary = parse_response(raw)
    except ValueError as e:
        log(f"{label}response validation failed: {e}")
        print(f"error: {e}", file=sys.stderr)
        return 1

    target = resolve_collision(archive_dir, filename)
    if target.name != filename:
        log(f"{label}collision resolved: {filename} -> {target.name}")

    title = topic_title_from_filename(target.name)
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    backup_dest = backup_dir / f"{stamp}-small-bank.md"
    archive_link = os.path.relpath(backup_dest, target.parent)

    try:
        write_archive(target, title, branch, sessions, summary, archive_link)
        log(f"{label}wrote {target}")
    except Exception as e:
        log(f"{label}archive write failed: {e}")
        print(f"error: archive write failed: {e}", file=sys.stderr)
        return 1

    try:
        backup = backup_source(source, backup_dir, stamp)
        log(f"{label}backed up source -> {backup}")
    except Exception as e:
        log(f"{label}backup failed (preserving source): {e}")
        print(f"error: backup failed, source preserved: {e}", file=sys.stderr)
        try:
            target.unlink()
            log(f"{label}rolled back archive write: {target}")
        except Exception:
            pass
        return 1

    try:
        source.unlink()
        log(f"{label}deleted source {source}")
    except Exception as e:
        log(f"{label}source delete failed: {e}")
        print(f"warning: source delete failed: {e}", file=sys.stderr)
        return 1

    print(f"{label}graduated -> {target}")
    return 0


def main(argv):
    try:
        args = parse_args(argv)
    except SystemExit as e:
        return int(e.code) if isinstance(e.code, int) else 2

    branch = detect_branch(args.branch)

    if args.subscriptions:
        try:
            banks = load_banks(args.subscriptions)
        except Exception as e:
            print(f"error: failed to load subscriptions: {e}", file=sys.stderr)
            return 1
        overall = 0
        for bank in banks:
            archive_dir = bank_archive_dir(bank)
            source = Path(bank["bank"]) / "small-bank.md"
            backup_dir = archive_dir / "small-bank-archive"
            ret = graduate_one(source, archive_dir, backup_dir, branch, bank.get("name", ""))
            if ret != 0:
                overall = ret
        return overall

    if not args.source or not args.archive_dir or not args.backup_dir:
        print("error: provide --subscriptions or all of --source/--archive-dir/--backup-dir", file=sys.stderr)
        return 2

    return graduate_one(
        Path(args.source),
        Path(args.archive_dir),
        Path(args.backup_dir),
        branch,
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
