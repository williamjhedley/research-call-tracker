"""
check_news.py  —  Phase 3: thesis news monitor
-----------------------------------------------
For each call in positions.csv, fetches recent news headlines (via yfinance) and
asks Claude whether each headline SUPPORTS, CHALLENGES, or is NEUTRAL to your
stated thesis. This is the part that "flags news supporting or challenging each
thesis."

SETUP (same key as Phase 2; plus one library):
    python -m pip install anthropic yfinance

USAGE:
    python check_news.py            # checks every call in positions.csv
    python check_news.py DPLM.L     # checks just one ticker

Cost: a few cents per run (one short Claude call per headline assessed).
"""

import sys
import csv
import datetime as dt

POSITIONS_FILE = "positions.csv"
MODEL = "claude-sonnet-4-6"
MAX_HEADLINES = 5          # per ticker, keeps cost + noise down


def load_positions():
    with open(POSITIONS_FILE, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def get_headlines(ticker):
    import yfinance as yf
    try:
        items = yf.Ticker(ticker).news or []
    except Exception as e:
        print(f"  (could not fetch news: {e})")
        return []
    heads = []
    for it in items[:MAX_HEADLINES]:
        # yfinance news item shape varies; handle both old and new layouts
        content = it.get("content", it)
        title = content.get("title") or it.get("title")
        if title:
            heads.append(title)
    return heads


def assess(client, thesis, rating, headline):
    prompt = (
        f"My investment call is a {rating}. My thesis: \"{thesis}\".\n"
        f"News headline: \"{headline}\".\n\n"
        "Does this headline SUPPORT, CHALLENGE, or is it NEUTRAL to my thesis? "
        "Answer with one word (SUPPORT, CHALLENGE, or NEUTRAL), then a dash and "
        "a max-15-word reason. Example: 'CHALLENGE - signals demand slowing, "
        "undercutting the growth assumption.'"
    )
    msg = client.messages.create(
        model=MODEL, max_tokens=80,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


def main():
    import anthropic
    client = anthropic.Anthropic()   # uses ANTHROPIC_API_KEY env var

    only = sys.argv[1].upper() if len(sys.argv) > 1 else None
    rows = load_positions()
    print(f"\nThesis news monitor  —  {dt.date.today()}\n")

    for r in rows:
        if only and r["ticker"].upper() != only:
            continue
        print(f"=== {r['ticker']}  ({r['rating']}) ===")
        print(f"    thesis: {r['thesis']}")
        heads = get_headlines(r["ticker"])
        if not heads:
            print("    no recent headlines found.\n")
            continue
        for h in heads:
            verdict = assess(client, r["thesis"], r["rating"], h)
            flag = "!!" if verdict.upper().startswith("CHALLENGE") else "  "
            print(f"  {flag} {h}")
            print(f"       -> {verdict}")
        print()

    print("Headlines marked !! challenge your thesis and are worth a closer look.\n")


if __name__ == "__main__":
    main()
