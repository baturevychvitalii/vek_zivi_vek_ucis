#!/usr/bin/env python3
"""Analyze Español deck statistics from AnkiConnect."""

import json
import urllib.request
import urllib.error
from collections import defaultdict
from datetime import datetime, timezone, timedelta

ANKI_URL = "http://localhost:8765"


def anki(action, **params):
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    req = urllib.request.Request(ANKI_URL, payload)
    with urllib.request.urlopen(req) as r:
        result = json.loads(r.read())
    if result["error"]:
        raise RuntimeError(result["error"])
    return result["result"]


def main():
    # --- Card info ---
    card_ids = anki("findCards", query="deck:Español")
    cards_info = anki("cardsInfo", cards=card_ids)

    total = len(cards_info)
    new_cards = sum(1 for c in cards_info if c["queue"] == 0)
    learning = sum(1 for c in cards_info if c["queue"] in (1, 3))
    young = sum(1 for c in cards_info if c["queue"] == 2 and c["interval"] < 21)
    mature = sum(1 for c in cards_info if c["queue"] == 2 and c["interval"] >= 21)
    suspended = sum(1 for c in cards_info if c["queue"] == -1)
    buried = sum(1 for c in cards_info if c["queue"] in (-2, -3))

    ease_factors = [c["factor"] / 10 for c in cards_info if c["queue"] == 2]
    avg_ease = sum(ease_factors) / len(ease_factors) if ease_factors else 0
    low_ease = sum(1 for e in ease_factors if e < 200)  # below 2.0 = struggling

    intervals = [c["interval"] for c in cards_info if c["queue"] == 2]
    avg_interval = sum(intervals) / len(intervals) if intervals else 0

    # --- Review history ---
    reviews = anki("cardReviews", deck="Español", startID=0)
    # fields: [reviewTime, cardID, usn, buttonPressed, newInterval, prevInterval, newFactor, duration, type]
    # buttonPressed: 1=Again, 2=Hard, 3=Good, 4=Easy
    # type: 0=learn, 1=review, 2=relearn

    total_reviews = len(reviews)
    button_counts = defaultdict(int)
    daily_reviews = defaultdict(int)
    daily_again = defaultdict(int)
    review_durations = []
    relearn_count = 0

    for r in reviews:
        ts, card_id, usn, btn, new_iv, prev_iv, new_factor, duration, rtype = r
        button_counts[btn] += 1
        day = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).date()
        daily_reviews[day] += 1
        if btn == 1:
            daily_again[day] += 1
        if rtype == 2:
            relearn_count += 1
        if duration > 0:
            review_durations.append(duration / 1000)  # ms -> s

    again = button_counts[1]
    hard = button_counts[2]
    good = button_counts[3]
    easy = button_counts[4]
    retention = (total_reviews - again) / total_reviews * 100 if total_reviews else 0

    avg_duration = sum(review_durations) / len(review_durations) if review_durations else 0

    # Cards that have been relearned (struggled with)
    relearn_cards = defaultdict(int)
    for r in reviews:
        ts, card_id, usn, btn, new_iv, prev_iv, new_factor, duration, rtype = r
        if rtype == 2:
            relearn_cards[card_id] += 1
    most_relearned = sorted(relearn_cards.items(), key=lambda x: -x[1])[:5]

    # Daily activity over last 30 days
    today = datetime.now(tz=timezone.utc).date()
    days_active_30 = sum(1 for d, c in daily_reviews.items()
                         if (today - d).days <= 30 and c > 0)
    avg_daily_30 = sum(c for d, c in daily_reviews.items()
                       if (today - d).days <= 30) / 30

    # Retention per day (last 14 days)
    print("=" * 60)
    print("ESPAÑOL DECK — LEARNING ANALYTICS")
    print("=" * 60)

    print(f"\n📦 CARD INVENTORY ({total} total)")
    print(f"  New (unseen):     {new_cards:>4}")
    print(f"  Learning:         {learning:>4}")
    print(f"  Young (<21d):     {young:>4}")
    print(f"  Mature (≥21d):    {mature:>4}")
    print(f"  Suspended:        {suspended:>4}")
    print(f"  Buried:           {buried:>4}")

    print(f"\n📊 REVIEW HISTORY ({total_reviews} total reviews)")
    print(f"  Again (forgot):   {again:>5}  ({again/total_reviews*100:.1f}%)")
    print(f"  Hard:             {hard:>5}  ({hard/total_reviews*100:.1f}%)")
    print(f"  Good:             {good:>5}  ({good/total_reviews*100:.1f}%)")
    print(f"  Easy:             {easy:>5}  ({easy/total_reviews*100:.1f}%)")
    print(f"  Overall retention:{retention:>6.1f}%")
    print(f"  Relearn events:   {relearn_count:>5}")
    print(f"  Avg time/card:    {avg_duration:>5.1f}s")

    print(f"\n📅 ACTIVITY")
    print(f"  Days active (last 30): {days_active_30}/30")
    print(f"  Avg reviews/day (30d): {avg_daily_30:.1f}")

    print(f"\n⚖️  CARD HEALTH")
    print(f"  Avg ease factor:  {avg_ease:.0f}%")
    print(f"  Low-ease cards (<200%): {low_ease}  ({low_ease/len(ease_factors)*100:.1f}% of reviews)" if ease_factors else "  No review cards yet")
    print(f"  Avg interval:     {avg_interval:.0f} days")

    print(f"\n🔁 MOST RELEARNED CARDS (struggled with)")
    if most_relearned:
        card_id_list = [cid for cid, _ in most_relearned]
        info_map = {c["cardId"]: c for c in anki("cardsInfo", cards=card_id_list)}
        for cid, count in most_relearned:
            c = info_map.get(cid, {})
            front = c.get("fields", {})
            # get first field value
            first_field = next(iter(front.values()), {}).get("value", str(cid)) if front else str(cid)
            # strip html
            import re
            first_field = re.sub(r"<[^>]+>", "", first_field)[:50]
            print(f"  {count}x  {first_field}")
    else:
        print("  None")

    print(f"\n💡 PATTERNS & SUGGESTIONS")

    if retention < 85:
        print(f"  ⚠ Retention {retention:.1f}% is below the healthy 85-90% target.")
        print(f"    Consider reviewing fewer new cards per day to reduce load.")
    elif retention > 95:
        print(f"  ✓ Retention {retention:.1f}% is high — you could safely introduce more new cards.")
    else:
        print(f"  ✓ Retention {retention:.1f}% is in a healthy range.")

    if low_ease > 0 and ease_factors:
        pct = low_ease / len(ease_factors) * 100
        if pct > 15:
            print(f"  ⚠ {pct:.0f}% of cards have ease <200% — these are \"leeches\" draining session time.")
            print(f"    Consider rewriting those cards to be more memorable or atomic.")

    if avg_duration > 20:
        print(f"  ⚠ Avg {avg_duration:.0f}s/card is high — you may be overthinking answers.")
    elif avg_duration < 5:
        print(f"  ⚠ Avg {avg_duration:.0f}s/card is very fast — are you reading cards carefully?")

    if days_active_30 < 25:
        print(f"  ⚠ Only {days_active_30} active days in the last 30 — consistency is the #1 factor in SRS.")
    else:
        print(f"  ✓ {days_active_30}/30 days active — strong consistency streak.")

    hard_rate = hard / total_reviews * 100 if total_reviews else 0
    if hard_rate > 20:
        print(f"  ⚠ {hard_rate:.0f}% Hard rate is elevated — cards may be too complex or ambiguous.")

    easy_rate = easy / total_reviews * 100 if total_reviews else 0
    if easy_rate > 30:
        print(f"  ✓ High Easy rate ({easy_rate:.0f}%) — many cards well-internalized.")

    print()


if __name__ == "__main__":
    main()
