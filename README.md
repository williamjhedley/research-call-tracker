# Research Call Tracker

I have recently been writing a few equity research reports and wanted a
way to check whether my calls actually hold up over time. So I built this.

It does three things:

* **tracker.py** reads my calls from a CSV, pulls live prices, and scores each one
against the FTSE. Did the stock beat, match, or lag the market since I made the call?
* **add\_report.py** reads one of my research docs and uses the Claude API to pull out
the rating, price target and thesis, so I'm not retyping it by hand.
* **check\_news.py** grabs recent news on each stock and asks Claude whether each
headline supports or challenges my thesis. The ones that challenge it get flagged.

On scoring: a BUY counts as right if the stock beat the market, a SELL if it lagged,
and a HOLD if it roughly matched (within about 5%). It's a rough proxy and doesn't
account for time horizon or risk yet, which is the main thing I'd improve.

## Running it

```
pip install yfinance pandas anthropic python-docx pypdf
```

Set your Claude API key as an environment variable (don't hard-code it):

```
setx ANTHROPIC\_API\_KEY "your-key"
```

Then:

```
python tracker.py
python add\_report.py "my\_report.docx" DPLM.L
python check\_news.py
```

Built with Python, yfinance for the price data, and the Claude API for the document
and news parts. It's a personal project, so the hit rate only really means anything
once there are a good number of calls in there.

