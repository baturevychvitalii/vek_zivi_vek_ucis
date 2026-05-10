"""
Health-agent test suite.
Run from project root: python3 .claude/health-agent/tests/test_health_agent.py

Covers:
  - Detector unit tests (all 6 modules)
  - End-to-end integration: actual hook script writes findings to real subsystem paths
"""

import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone, timedelta

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
SUBSYSTEM_DIR = os.path.dirname(TESTS_DIR)
CLAUDE_DIR = os.path.dirname(SUBSYSTEM_DIR)
PROJECT_ROOT = os.path.dirname(CLAUDE_DIR)

sys.path.insert(0, SUBSYSTEM_DIR)
from detectors import (
    bash_chaining, git_policy, destructive_ops,
    whitelist_gap, skill_circumvention, refactoring_rot,
)

PASS = []
FAIL = []


def check(label, condition):
    if condition:
        PASS.append(label)
        print(f"  PASS  {label}")
    else:
        FAIL.append(label)
        print(f"  FAIL  {label}")


# --- context factory ---

def ctx(tool_uses=None, tool_results=None, permission_events=None, claude_dir=None):
    return {
        "skill": "test-skill",
        "started_at": datetime.now(timezone.utc),
        "transcript_path": "",
        "tool_uses": tool_uses or [],
        "tool_results": tool_results or [],
        "permission_events": permission_events or [],
        "claude_dir": claude_dir or CLAUDE_DIR,
    }


def bash(cmd):
    return {"name": "Bash", "id": "tu_test", "input": {"command": cmd}}


def edit(file_path, content):
    return {"name": "Edit", "id": "tu_edit", "input": {"file_path": file_path, "new_string": content}}


# --- detector unit tests ---

def test_bash_chaining():
    print("\n[bash_chaining]")
    r = bash_chaining.detect(ctx([bash("git log && echo done")]))
    check("&& → violation", any(f["rule"] == "bash_chaining" for f in r))

    r = bash_chaining.detect(ctx([bash("cat file.txt | grep foo")]))
    check("| → pipe warning", any(f["rule"] == "bash_chaining_pipe" for f in r))

    r = bash_chaining.detect(ctx([bash("mkdir /tmp/x; rm /tmp/x")]))
    check("; → violation", any(f["rule"] == "bash_chaining" for f in r))

    r = bash_chaining.detect(ctx([bash("python3 .claude/scripts/anki.py 'hello'")]))
    check("clean command → no findings", r == [])

    r = bash_chaining.detect(ctx([bash("git log --oneline -5")]))
    check("git log → not flagged", r == [])


def test_git_policy():
    print("\n[git_policy]")
    r = git_policy.detect(ctx([bash("git commit -m 'msg'")]))
    check("git commit → violation", any(f["rule"] == "git_policy" for f in r))

    r = git_policy.detect(ctx([bash("git push origin main")]))
    check("git push → violation", any(f["rule"] == "git_policy" for f in r))

    r = git_policy.detect(ctx([bash("git add .")]))
    check("git add → violation", any(f["rule"] == "git_policy" for f in r))

    r = git_policy.detect(ctx([bash("git reset --hard HEAD")]))
    check("git reset --hard → violation", any(f["rule"] == "git_policy" for f in r))

    r = git_policy.detect(ctx([bash("git log --oneline -5")]))
    check("git log → no findings", r == [])

    r = git_policy.detect(ctx([bash("git diff HEAD")]))
    check("git diff → no findings", r == [])


def test_destructive_ops():
    print("\n[destructive_ops]")
    r = destructive_ops.detect(ctx([bash("rm -rf /tmp/test")]))
    check("rm -rf → violation", any(f["rule"] == "destructive_ops" for f in r))

    r = destructive_ops.detect(ctx([bash("git commit --no-verify -m 'msg'")]))
    check("--no-verify → violation", any(f["rule"] == "destructive_ops" for f in r))

    r = destructive_ops.detect(ctx([bash("git push --force origin main")]))
    check("git push --force → violation", any(f["rule"] == "destructive_ops" for f in r))

    r = destructive_ops.detect(ctx([bash("ls -la .claude/")]))
    check("ls → no findings", r == [])


def test_whitelist_gap():
    print("\n[whitelist_gap]")
    # Event not in settings.json allowlist → warning
    ev_missing = {"tool_name": "Bash", "detail": "python3 .claude/scripts/mystery.py foo"}
    r = whitelist_gap.detect(ctx(permission_events=[ev_missing]))
    check("unmatched event → warning", any(f["rule"] == "whitelist_gap" for f in r))

    # Event that IS in the allowlist → no findings
    ev_allowed = {"tool_name": "Bash", "detail": "python3 .claude/scripts/anki.py arg1"}
    r = whitelist_gap.detect(ctx(permission_events=[ev_allowed]))
    check("allowlisted event → no findings", r == [])

    # No events → no findings
    r = whitelist_gap.detect(ctx(permission_events=[]))
    check("no events → no findings", r == [])


def test_skill_circumvention():
    print("\n[skill_circumvention]")
    skill_use = {"name": "Skill", "id": "tu_skill", "input": {"skill": "anki-add"}}
    failed = {"tool_use_id": "tu_skill", "is_error": True, "content": "skill not found"}
    spec_read = {"name": "Read", "id": "tu_r", "input": {"file_path": ".claude/commands/anki-add.md"}}

    r = skill_circumvention.detect(ctx(tool_uses=[skill_use, spec_read], tool_results=[failed]))
    check("failed skill + spec read → anomaly", any(f["rule"] == "skill_circumvention" for f in r))

    ok = {"tool_use_id": "tu_skill", "is_error": False, "content": "done"}
    r = skill_circumvention.detect(ctx(tool_uses=[skill_use, spec_read], tool_results=[ok]))
    check("successful skill → no findings", r == [])

    r = skill_circumvention.detect(ctx(tool_uses=[skill_use], tool_results=[failed]))
    check("failed skill, no subsequent reads → no findings", r == [])


def test_refactoring_rot():
    print("\n[refactoring_rot]")
    # Edit to a skill file referencing a nonexistent path
    bad_edit = edit(
        ".claude/commands/test-skill.md",
        "run `python3 '.claude/scripts/does-not-exist-xyz.py'`",
    )
    r = refactoring_rot.detect(ctx([bad_edit]))
    check("broken .claude/ path ref → warning", any(f["rule"] == "refactoring_rot" for f in r))

    # Edit to a skill file referencing a path that exists
    good_edit = edit(
        ".claude/commands/test-skill.md",
        "run `python3 '.claude/scripts/anki.py'`",
    )
    r = refactoring_rot.detect(ctx([good_edit]))
    check("valid .claude/ path ref → no findings", r == [])

    # Edit outside tracked targets → not scanned
    outside = edit("/home/user/random.md", "'.claude/scripts/does-not-exist-xyz.py'")
    r = refactoring_rot.detect(ctx([outside]))
    check("edit outside tracked targets → no findings", r == [])

    # Broken skill reference inside a pipeline spec
    bad_skill_edit = edit(
        ".claude/pipeline-specifications/test.md",
        "skill: 'pipe:nonexistent-skill-xyz'",
    )
    r = refactoring_rot.detect(ctx([bad_skill_edit]))
    check("missing skill ref → warning", any(f["rule"] == "refactoring_rot" for f in r))


# --- end-to-end integration test ---

def test_e2e_detection():
    """
    Runs the actual detect-health-issues.py hook script against a synthetic transcript
    that contains one bash_chaining violation and one git_policy violation.
    Verifies that findings land at the real subsystem paths.
    """
    print("\n[e2e: detect-health-issues hook]")

    summary_path = os.path.join(SUBSYSTEM_DIR, "run-summary.json")
    findings_path = os.path.join(SUBSYSTEM_DIR, "health-findings.jsonl")
    flag_path = os.path.join(SUBSYSTEM_DIR, "pending-ai-review.flag")
    hook_path = os.path.join(SUBSYSTEM_DIR, "hooks", "detect-health-issues.py")

    # Back up existing state
    old_summary = None
    if os.path.exists(summary_path):
        with open(summary_path) as f:
            old_summary = f.read()

    old_findings_lines = []
    if os.path.exists(findings_path):
        with open(findings_path) as f:
            old_findings_lines = f.readlines()

    flag_existed = os.path.exists(flag_path)

    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False
        ) as tf:
            transcript_path = tf.name
            started_at = (datetime.now(timezone.utc) - timedelta(seconds=10)).isoformat()
            # One bash_chaining violation
            tf.write(json.dumps({
                "type": "assistant",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": {"content": [
                    {"type": "tool_use", "name": "Bash", "id": "tu1",
                     "input": {"command": "git log && echo done"}},
                    {"type": "tool_use", "name": "Bash", "id": "tu2",
                     "input": {"command": "git add ."}},
                ]}
            }) + "\n")

        with open(summary_path, "w") as f:
            json.dump({
                "skill": "test-e2e",
                "started_at": started_at,
                "transcript_path": transcript_path,
            }, f)

        result = subprocess.run(
            ["python3", hook_path],
            input="",
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        check("hook exits 0", result.returncode == 0)
        if result.returncode != 0:
            print(f"    stderr: {result.stderr[:400]}")
            return

        # run-summary should have analyzed_at stamped
        with open(summary_path) as f:
            stamped = json.load(f)
        check("analyzed_at stamped in run-summary", "analyzed_at" in stamped)

        # New findings should have been appended
        with open(findings_path) as f:
            new_lines = f.readlines()
        new_findings = [json.loads(l) for l in new_lines[len(old_findings_lines):]]
        check("findings appended", len(new_findings) > 0)

        new_rules = [f["rule"] for f in new_findings]
        check("bash_chaining detected", "bash_chaining" in new_rules)
        check("git_policy detected", "git_policy" in new_rules)
        check("skill field set", all(f["skill"] == "test-e2e" for f in new_findings))
        check("status=unreviewed", all(f["status"] == "unreviewed" for f in new_findings))

        # Pending flag should exist
        check("pending flag created", os.path.exists(flag_path))

        # Hook is idempotent: re-running skips already-analyzed summary
        result2 = subprocess.run(
            ["python3", hook_path],
            input="",
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        with open(findings_path) as f:
            after_second_run = f.readlines()
        check("idempotent: no double-write", len(after_second_run) == len(new_lines))

    finally:
        os.unlink(transcript_path)

        # Restore findings (strip test entries)
        with open(findings_path, "w") as f:
            f.writelines(old_findings_lines)

        # Restore run-summary
        if old_summary is not None:
            with open(summary_path, "w") as f:
                f.write(old_summary)
        elif os.path.exists(summary_path):
            os.unlink(summary_path)

        # Restore flag state
        if not flag_existed and os.path.exists(flag_path):
            os.unlink(flag_path)


# --- run ---

test_bash_chaining()
test_git_policy()
test_destructive_ops()
test_whitelist_gap()
test_skill_circumvention()
test_refactoring_rot()
test_e2e_detection()

print(f"\n{'='*50}")
print(f"Results: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("Failed:")
    for label in FAIL:
        print(f"  - {label}")
    sys.exit(1)
else:
    print("All tests passed.")
