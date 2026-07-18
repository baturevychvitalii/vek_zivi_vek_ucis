#!/usr/bin/env python3
"""Deterministic crawler: CVUT bílá kniha faculty subject list -> CSV.

Phase 1 of the CVUT per-subject outreach. Emits one row per subject with the
detail-page link (mandatory column), the guarantor + their usermap profile,
co-teachers, and the owning department. Subject *descriptions* are deliberately
deferred to phase 2 — this pass only collects the roster from the listing table.

The flat "Všechny předměty fakulty" page (e.g. f8-predmety.html) is a complete
superset of every department page and the faculty electives page for that
faculty, so one page + one parser covers a whole faculty. Verified 2026-07-17:
all 774 katedra codes and all 154 f8-volitelne codes are already in f8-predmety.

Usage:
    python3 scrape_subjects.py --faculty FIT --page f8-predmety.html -o subjects.csv
    python3 scrape_subjects.py --faculty FIT --page f8-predmety.html --from-file cached.html -o subjects.csv
"""
import argparse
import csv
import sys
import urllib.request

from bs4 import BeautifulSoup

BASE = "https://bilakniha.cvut.cz/cs/"

FIELDS = [
    "code",
    "name",
    "detail_url",
    "guarantor",
    "guarantor_profile",
    "teachers",
    "department",
    "faculty",
    "language",
    "completion",
    "credits",
]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        return r.read().decode("utf-8")


def cell_text(cells, i):
    """Text of the i-th <td>, or '' when the row is short."""
    return cells[i].get_text(strip=True) if i < len(cells) else ""


def parse(html, faculty):
    """Parse the flat listing table into subject dicts, one per row."""
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", class_="seznam.predmetu")
    if table is None:
        raise SystemExit("no subject table (class 'seznam.predmetu') on page")

    rows = []
    for tr in table.find("tbody").find_all("tr", recursive=False):
        cells = tr.find_all("td", recursive=False)
        if len(cells) < 4:
            continue  # separator / group-header rows

        name_a = cells[1].find("a")
        if name_a is None or not name_a.get("href"):
            continue  # no detail link -> not a real subject row
        detail_url = BASE + name_a["href"]

        # Teacher cell: the guarantor is the <a> immediately before the
        # <sup class="garant-flag"> (Ⓖ); everyone else is a co-teacher.
        teacher_cell = cells[2]
        guarantor = guarantor_profile = ""
        flag = teacher_cell.find("sup", class_="garant-flag")
        if flag is not None:
            g = flag.find_previous_sibling("a")
            if g is not None:
                guarantor = g.get_text(strip=True)
                guarantor_profile = g.get("href", "")
        teachers = "; ".join(a.get_text(strip=True) for a in teacher_cell.find_all("a"))

        rows.append({
            "code": cell_text(cells, 0),
            "name": name_a.get_text(strip=True),
            "detail_url": detail_url,
            "guarantor": guarantor,
            "guarantor_profile": guarantor_profile,
            "teachers": teachers,
            "department": cell_text(cells, 3),
            "faculty": faculty,
            "language": cell_text(cells, 4),
            "completion": cell_text(cells, 5),
            "credits": cell_text(cells, 6),
        })
    return rows


def dedup(rows):
    """Dedup by subject code (first-seen wins), then sort by code."""
    seen = {}
    for r in rows:
        seen.setdefault(r["code"], r)
    return sorted(seen.values(), key=lambda r: r["code"])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--faculty", required=True, help="short label stamped into every row, e.g. FIT")
    ap.add_argument("--page", required=True, help="listing page basename, e.g. f8-predmety.html")
    ap.add_argument("--from-file", help="parse this local HTML instead of fetching (offline / deterministic)")
    ap.add_argument("-o", "--out", required=True, help="output CSV path")
    args = ap.parse_args()

    if args.from_file:
        html = open(args.from_file, encoding="utf-8").read()
    else:
        html = fetch(BASE + args.page)

    rows = dedup(parse(html, args.faculty))

    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    print(f"wrote {len(rows)} subjects -> {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
