# Research Call Tracker

A Python tool that tracks my independent equity-research calls against the market
and uses an LLM to flag news that supports or challenges each thesis.

I publish my own equity-research notes (e.g. a HOLD on Diploma plc). This tool
exists to answer two questions a real analyst lives by: **were my calls actually
right?** and **is new information moving for or against my thesis?**

## What it does

The tool has three parts:

1. **Tracker** (`tracker.py`) — reads my calls from `positions.csv`, pulls live
   prices via `yfinance`, and scores each call against a benchmark (FTSE 100).
   It reports each call's return, the market's return over the same period, the
   relative performance, and a verdict.

2. **AI report reader** (`add_report.py`) — reads one of my research documents
   (.docx / .pdf / .txt), uses the Claude API to extract the rating, price target
   and a one-line thesis, and appends it to `positions.csv`. This means a new call
   is logged from the source document rather than typed by hand.

3. **Thesis news monitor** (`check_news.py`) — for each call, fetches recent news
   headlines and asks Claude whether each one *supports*, *challenges*, or is
   *neutral* to my stated thesis, flagging the challenging ones.

## The scoring rule

The interesting design decision is what counts as a call being "right". I score
each call's return *relative to the benchmark*:

- **BUY**  — right if the stock beat the market
- **SELL** — right if the stock lagged the market
- **HOLD** — right if the stock roughly matched the market (within ±5 percentage
  points). A HOLD that lagged a rising stock is flagged "too cautious"; a HOLD on
  a stock that fell behind is flagged "too bullish".

This is deliberately simple. It's a relative-return proxy and does **not** adjust
for holding period or risk — a known limitation I'd refine in a later version.

## Example output

```
Ticker  Call      Base      Now   Stock%    Mkt%    Rel%  Verdict
-----------------------------------------------------------------
DPLM.L  HOLD      6885     7135     +3.6    -0.7    +4.3  RIGHT
```

```
=== DPLM.L  (HOLD) ===
  !! Analysts lift Diploma price target
       -> CHALLENGE - upgrade suggests valuation may be justified,
          undermining the "already priced in" argument.
```

## Setup

```bash
pip install yfinance pandas anthropic python-docx pypdf
```

The AI parts use the Claude API. Set your key as an environment variable
(never hard-code it):

```bash
# Windows
setx ANTHROPIC_API_KEY "your-key-here"
# macOS / Linux
export ANTHROPIC_API_KEY="your-key-here"
```

## Usage

```bash
python tracker.py                                  # score all calls
python add_report.py "my_report.docx" DPLM.L       # log a call from a report
python check_news.py                               # flag thesis-relevant news
```

## Tech

Python, yfinance (market data), Anthropic Claude API (extraction + news
classification), python-docx / pypdf (document reading).

## Notes

Built as a personal project to support my own research process. The hit-rate is
only meaningful over many calls; a single call is one data point, not a track
record.
