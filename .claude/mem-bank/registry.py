import json
import re
from pathlib import Path


def load_banks(subs_path, cwd=None):
    path = Path(subs_path)
    if cwd and not path.is_absolute():
        path = Path(cwd) / path
    with open(path) as f:
        data = json.load(f)
    return data.get("banks", [])


def bank_effective_patterns(bank_cfg):
    if "patterns" in bank_cfg:
        return list(bank_cfg["patterns"])
    if "pattern" in bank_cfg:
        return [bank_cfg["pattern"]]
    return [re.escape(bank_cfg["bank"]) + r"/context\.md"]


def bank_small_bank_path(bank_cfg, cwd=None):
    p = Path(bank_cfg["bank"]) / "small-bank.md"
    if cwd and not p.is_absolute():
        p = Path(cwd) / p
    return p


def bank_archive_dir(bank_cfg):
    return Path(bank_cfg["bank"]) / "big-bank"


def populated_banks(banks, cwd=None):
    result = []
    for bank in banks:
        path = bank_small_bank_path(bank, cwd)
        if path.exists() and path.read_text().strip():
            result.append((bank, path))
    return result
