# Research Call Tracker

I have recently been writing my own equity research and wanted a
way to check whether my calls actually hold up over time. So I built this.

It does three things:

- **tracker.py** reads my calls from a CSV, pulls live prices, and scores each one
  against the FTSE. Did the stock beat, match, or lag the market since I made the call?
- **add_report.py** reads one of my research docs and uses the Claude API to pull out
  the rating, price target and thesis, so I'm not retyping it by hand.
- **check_news.py** grabs recent news on each stock and asks Claude whether each
  headline supports or challenges my thesis. The ones that challenge it get flagged.

On scoring: a BUY counts as right if the stock beat the market, a SELL if it lagged,
and a HOLD if it roughly matched (within about 5%). It's a rough proxy and doesn't
account for time horizon or risk yet, which is the main thing I'd improve.

## How to run it

You will need to have Python installed (I used version 3.14 https://www.python.org/downloads/). Then there are three one-time setup steps, after
which you just run the scripts.

**1. Install the libraries.** These handle the market data, the spreadsheet, the
Claude API, and reading Word/PDF files:

```
pip install yfinance pandas anthropic python-docx pypdf
```

**2. Add your Claude API key.** The two AI scripts call Claude, so they need a key
from console.anthropic.com. Set it as an environment variable rather than writing
it into the code (so it never ends up public):

```
setx ANTHROPIC_API_KEY "your-key-here"
```

On Windows, close and reopen your terminal after this so it takes effect. (On Mac
or Linux, use `export ANTHROPIC_API_KEY="your-key-here"` instead.)

**3. Add your calls.** Each row in `positions.csv` is one research call:
ticker, company, date, rating, entry price, target, and a one-line thesis. You can
fill it in by hand, or let `add_report.py` do it from a report (next section).

**Then run whichever part you want:**

Score all your current calls against the market:
```
python tracker.py
```

Read a research document and add it as a call automatically:
```
python add_report.py "my_report.docx" DPLM.L
```
(the second argument is the ticker, in Yahoo Finance format — UK stocks end in `.L`)

Check recent news against each thesis:
```
python check_news.py
```

## Built with

Python, yfinance for the price data, and the Claude API for the document parsing
and news checks. It's a personal project, so the hit rate only really means
anything once there are a good number of calls in there.
