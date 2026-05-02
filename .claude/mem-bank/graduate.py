import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent / "mem-bank.log"
SCRIPT_TAG = "[mem-bank-graduate]"

FILENAME_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*\.md$")
SESSION_HEADER_RE = re.compile(
    r"^## \d{4}-\d{2}-\d{2} \d{2}:\d{2} \(session ([a-zA-Z0-9]+)\)",
    re.MULTILINE,
)


def log(detail):
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "a") as f:
            f.write(f"{datetime.now().isoformat()}\t{SCRIPT_TAG}\t{detail}\n")
    except Exception:
        pass


def parse_args(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--archive-dir", required=True)
    p.add_argument("--backup-dir", required=True)
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
        "INPUT — active-context.md from the branch:\n"
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
    env = os.environ.copy()
    env["MEM_BANK_HOOK_RECURSION_GUARD"] = "1"
    result = subprocess.run(
        ["claude", "-p", "--model", "sonnet", prompt],
        capture_output=True, text=True, timeout=300, env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude exited {result.returncode}: {result.stderr.strip()}")
    return result.stdout.strip()


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


def write_archive(target, title, branch, sessions, summary, source_text):
    sessions_str = ", ".join(sessions) if sessions else "n/a"
    today = datetime.now().strftime("%Y-%m-%d")
    body = (
        f"# {title}\n\n"
        f"<{today} — branch {branch} — sessions {sessions_str}>\n\n"
        f"## Summary\n{summary}\n\n"
        f"## Active context contents\n{source_text}"
    )
    if not body.endswith("\n"):
        body += "\n"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body)


def backup_source(source, backup_dir):
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    dest = backup_dir / f"{stamp}-active-context.md"
    shutil.copy2(source, dest)
    return dest


def main(argv):
    try:
        args = parse_args(argv)
    except SystemExit as e:
        return int(e.code) if isinstance(e.code, int) else 2

    source = Path(args.source)
    archive_dir = Path(args.archive_dir)
    backup_dir = Path(args.backup_dir)

    log(f"called: source={source} archive_dir={archive_dir} backup_dir={backup_dir} branch={args.branch!r}")

    if not source.exists():
        log("source missing — clean no-op")
        print(f"{source}: not found, nothing to graduate")
        return 0

    try:
        source_text = source.read_text()
    except Exception as e:
        log(f"failed to read source: {e}")
        print(f"error: failed to read {source}: {e}", file=sys.stderr)
        return 1

    if not source_text.strip():
        log("source empty — clean no-op")
        print(f"{source}: empty, nothing to graduate")
        return 0

    branch = detect_branch(args.branch)
    sessions = extract_sessions(source_text)

    archive_dir.mkdir(parents=True, exist_ok=True)
    existing = [p.name for p in archive_dir.glob("*.md")]

    prompt = build_prompt(source_text, branch, existing)

    try:
        raw = call_claude(prompt)
    except Exception as e:
        log(f"claude call failed: {e}")
        print(f"error: claude call failed: {e}", file=sys.stderr)
        return 1
    log(f"claude response ({len(raw)} chars)")

    try:
        filename, summary = parse_response(raw)
    except ValueError as e:
        log(f"response validation failed: {e}")
        print(f"error: {e}", file=sys.stderr)
        return 1

    target = resolve_collision(archive_dir, filename)
    if target.name != filename:
        log(f"collision resolved: {filename} -> {target.name}")

    title = topic_title_from_filename(target.name)

    try:
        write_archive(target, title, branch, sessions, summary, source_text)
        log(f"wrote {target}")
    except Exception as e:
        log(f"archive write failed: {e}")
        print(f"error: archive write failed: {e}", file=sys.stderr)
        return 1

    try:
        backup = backup_source(source, backup_dir)
        log(f"backed up source -> {backup}")
    except Exception as e:
        log(f"backup failed (preserving source): {e}")
        print(f"error: backup failed, source preserved: {e}", file=sys.stderr)
        try:
            target.unlink()
            log(f"rolled back archive write: {target}")
        except Exception:
            pass
        return 1

    try:
        source.unlink()
        log(f"deleted source {source}")
    except Exception as e:
        log(f"source delete failed: {e}")
        print(f"warning: source delete failed: {e}", file=sys.stderr)
        return 1

    print(f"graduated -> {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
