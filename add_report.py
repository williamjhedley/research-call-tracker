"""
add_report.py  —  Phase 2: AI report reader
--------------------------------------------
Reads one of your equity-research documents (.docx, .pdf, or .txt), uses Claude
to extract the rating / target / thesis, and appends a row to positions.csv so
tracker.py can score it. This is the part that makes the tool actually READ your
reports instead of you hand-typing the CSV.

ONE-TIME SETUP
--------------
1) Install libraries:
       python -m pip install anthropic python-docx pypdf

2) Get an API key from https://console.anthropic.com  (Settings -> API Keys),
   add some credit (a few dollars is plenty; each report costs ~1-3 cents),
   then set the key as an environment variable so it is NOT written in the code:

   Windows (Command Prompt), run once per terminal session:
       set ANTHROPIC_API_KEY=sk-ant-xxxxxxxx
   To set it permanently (so you don't retype it), run once:
       setx ANTHROPIC_API_KEY "sk-ant-xxxxxxxx"
   then close and reopen Command Prompt.

USAGE
-----
    python add_report.py "Diploma_PLC_Equity_Research.docx" DPLM.L
                          ^ path to your report           ^ ticker (Yahoo format)

The ticker is something only you know reliably, so you pass it in. Everything
else (rating, target, thesis, today's date) is extracted or filled automatically.
"""

import sys
import os
import csv
import datetime as dt
import json

POSITIONS_FILE = "positions.csv"
MODEL = "claude-sonnet-4-6"          # capable + cheap enough for this
COLUMNS = ["ticker", "company", "date_opened", "rating",
           "entry_price", "target_price", "thesis"]


# ---------- 1. read the document into plain text ----------
def read_document(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".txt":
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read()
    if ext == ".docx":
        import docx
        d = docx.Document(path)
        return "\n".join(p.text for p in d.paragraphs)
    if ext == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(path)
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    raise ValueError(f"Unsupported file type: {ext}. Use .docx, .pdf, or .txt")


# ---------- 2. ask Claude to extract the call ----------
def extract_call(text):
    import anthropic
    client = anthropic.Anthropic()   # reads ANTHROPIC_API_KEY from environment

    # keep token cost down: only send the first ~6000 words
    snippet = " ".join(text.split()[:6000])

    prompt = (
        "You are reading an equity research report. Extract these fields and "
        "respond with ONLY a JSON object, no other text:\n"
        '{\n'
        '  "company": "company name",\n'
        '  "rating": "BUY, HOLD or SELL (uppercase)",\n'
        '  "target_price": "numeric price target in pence or the report\'s unit, digits only, or null",\n'
        '  "thesis": "one sentence, max 25 words, summarising the core argument"\n'
        '}\n\n'
        "If a field is not stated, use null. Report text follows:\n\n" + snippet
    )

    msg = client.messages.create(
        model=MODEL,
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = msg.content[0].text.strip()
    # strip code fences if the model added them
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


# ---------- 3. append a row to positions.csv ----------
def append_row(row):
    file_exists = os.path.exists(POSITIONS_FILE)
    with open(POSITIONS_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, quoting=csv.QUOTE_MINIMAL)
        if not file_exists:
            w.writeheader()
        w.writerow(row)


def main():
    if len(sys.argv) < 3:
        print('Usage: python add_report.py "<report file>" <TICKER>')
        print('Example: python add_report.py "Diploma_PLC_Equity_Research.docx" DPLM.L')
        sys.exit(1)

    path, ticker = sys.argv[1], sys.argv[2].upper()
    print(f"Reading {path} ...")
    text = read_document(path)
    if len(text.strip()) < 50:
        print("Warning: very little text extracted. Is the file readable?")

    print("Asking Claude to extract the call ...")
    call = extract_call(text)

    row = {
        "ticker": ticker,
        "company": call.get("company") or ticker,
        "date_opened": dt.date.today().isoformat(),
        "rating": (call.get("rating") or "").upper(),
        "entry_price": "",                       # tracker measures from market close anyway
        "target_price": call.get("target_price") or "",
        "thesis": call.get("thesis") or "",
    }

    print("\nExtracted:")
    for k, v in row.items():
        print(f"  {k:<13}: {v}")

    ok = input("\nAdd this row to positions.csv? (y/n) ").strip().lower()
    if ok == "y":
        append_row(row)
        print("Added. Run  python tracker.py  to see the updated scorecard.")
    else:
        print("Cancelled. Nothing written.")


if __name__ == "__main__":
    main()
