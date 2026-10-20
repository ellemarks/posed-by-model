#!/usr/bin/env python3
# export GOOGLE_TRANSLATE_API_KEY
# python3 06-translate_ocr.py ../../data/04_format
import csv, os, re, sys, time, unicodedata
from pathlib import Path

import requests

TABLE = Path(__file__).resolve().parents[2] / "config" / "accounts.tsv"
LANG = {r["account"]: r["language"] for r in csv.DictReader(open(TABLE, encoding="utf-8"), delimiter="\t")}
MAX_CHARS = 800

# google
KEY = os.environ["GOOGLE_TRANSLATE_API_KEY"]
def google(text, source=None):
    data = {"q": text, "target": "en", "format": "text", "model": "nmt"}
    if source:
        data["source"] = source
    r = requests.post("https://translation.googleapis.com/language/translate/v2",
                      data=data, headers={"X-Goog-Api-Key": KEY}, timeout=60)
    r.raise_for_status()
    time.sleep(0.1)
    return r.json()["data"]["translations"][0]["translatedText"]

def plain(t):
    t = "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^0-9A-Za-z]+", " ", t).upper().split())

def to_english(text, source):
    english = google(text, source)
    if plain(english) == plain(text):
        english = google(text)
    return " ".join(english.split())

# capitals
def normal_case(text):
    words = [w for w in ("".join(c for c in tok if c.isalpha()) for tok in text.split()) if len(w) >= 2]
    if not words or sum(w.isupper() for w in words) / len(words) < 0.6:
        return text
    out, start = [], True
    for tok in re.split(r"(\s+)", text):
        alpha = "".join(c for c in tok if c.isalpha())
        if alpha.isupper() and not any(c.isdigit() for c in tok) \
                and any(c in "AEIOUY" for c in unicodedata.normalize("NFKD", alpha)):
            tok = tok.lower()
            if start:
                i = next(k for k, c in enumerate(tok) if c.isalpha())
                tok = tok[:i] + tok[i].upper() + tok[i + 1:]
        out.append(tok)
        if alpha:
            start = bool(re.search(r"[.!?…][\"'»”)\]]*$", tok))
    return "".join(out)

# files
root = Path(sys.argv[1])
for ocr in sorted(root.glob("*/*.ocr.txt")):
    account, stem = ocr.parent.name, ocr.name[:-len(".ocr.txt")]
    lines = [l.strip() for l in ocr.read_text(encoding="utf-8").splitlines() if l.strip()]
    original = "\n".join(lines)
    if LANG[account] == "en":
        ocr.with_name(stem + ".transcribed.txt").write_text(original + ("\n" if lines else ""), encoding="utf-8")
        continue
    one_line = " ".join(" ".join(lines).split())
    if not lines:
        english = ""
    elif len(one_line) > MAX_CHARS:
        english = "TRANSLATION N/A"
    elif not any(c.isalpha() for c in one_line):
        english = one_line  # numbers only
    else:
        english = to_english(normal_case(one_line), LANG[account])
    ocr.with_name(stem + ".translated.txt").write_text(
        f"=== ORIGINAL ===\n{original}\n\n=== TRANSLATED (EN) ===\n{english}\n", encoding="utf-8")
    print(f"{account}/{stem}: {len(lines)} lines")
