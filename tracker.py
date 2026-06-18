"""
Research Call Tracker  —  Phase 1 (Option A), v2
------------------------------------------------
Fix vs v1: the % change is now derived from the SAME prices shown, and the
baseline price actually used is printed, so every number reconciles and you
can sanity-check it by hand.

SETUP:  python -m pip install yfinance pandas
RUN:    python tracker.py
"""

import yfinance as yf
import pandas as pd
import datetime as dt

BENCHMARK = "^FTSE"
POSITIONS_FILE = "positions.csv"
HOLD_BAND = 5.0   # +/- percentage points for a HOLD to count as "matched the market"


def price_series(ticker, since_date):
    """Return (baseline_close, latest_close) using a single clean history pull."""
    hist = yf.Ticker(ticker).history(start=since_date, auto_adjust=True)
    if hist.empty or "Close" not in hist:
        return None
    closes = hist["Close"].dropna()
    if len(closes) < 1:
        return None
    return float(closes.iloc[0]), float(closes.iloc[-1])


def ret_pct(baseline, latest):
    return (latest - baseline) / baseline * 100.0


def verdict(rating, rel):
    rating = rating.upper()
    if rating == "BUY":
        return "RIGHT" if rel > 0 else "WRONG"
    if rating == "SELL":
        return "RIGHT" if rel < 0 else "WRONG"
    if rating == "HOLD":
        if abs(rel) <= HOLD_BAND:
            return "RIGHT"
        return "TOO CAUTIOUS" if rel > 0 else "TOO BULLISH"
    return "?"


def main():
    pos = pd.read_csv(POSITIONS_FILE)
    print(f"\nResearch Call Tracker  —  {dt.date.today()}  (benchmark: {BENCHMARK})\n")
    header = (f"{'Ticker':<8}{'Call':<6}{'Base':>8}{'Now':>9}"
              f"{'Stock%':>9}{'Mkt%':>8}{'Rel%':>8}  Verdict")
    print(header)
    print("-" * len(header))

    rights = scored = 0
    for _, r in pos.iterrows():
        start = r["date_opened"]
        stk = price_series(r["ticker"], start)
        bmk = price_series(BENCHMARK, start)
        if stk is None or bmk is None:
            print(f"{r['ticker']:<8}{r['rating']:<6}  (no price data)")
            continue

        s_base, s_now = stk
        b_base, b_now = bmk
        s_ret = ret_pct(s_base, s_now)
        b_ret = ret_pct(b_base, b_now)
        rel = s_ret - b_ret
        v = verdict(r["rating"], rel)
        scored += 1
        if v == "RIGHT":
            rights += 1

        print(f"{r['ticker']:<8}{r['rating']:<6}{s_base:>8.0f}{s_now:>9.0f}"
              f"{s_ret:>+9.1f}{b_ret:>+8.1f}{rel:>+8.1f}  {v}")

    print("-" * len(header))
    if scored:
        print(f"\nHit rate: {rights}/{scored} vindicated vs benchmark "
              f"({rights/scored*100:.0f}%)")
    print("\n'Base' = closing price on the date you opened the call (what % is measured from).")
    print("'TOO CAUTIOUS' = HOLD that lagged a rising stock; 'TOO BULLISH' = HOLD on a laggard.\n")


if __name__ == "__main__":
    main()
