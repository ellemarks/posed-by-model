#!/usr/bin/env python3
# Aided by Claude Opus 5
# export GOOGLE_TRANSLATE_API_KEY
# python3 05-translate_captions.py ../../data/04_format
import csv, os, re, sys, time, unicodedata
from pathlib import Path

import requests

MARK = "--- English Translation ---"
TABLE = Path(__file__).resolve().parents[2] / "config" / "accounts.tsv"
LANG = {r["account"]: r["language"] for r in csv.DictReader(open(TABLE, encoding="utf-8"), delimiter="\t")}
CATALAN = {"ES-EU_vox_es/2024-04-04_(3)", "ES-EU_vox_es/2024-04-04_(4)", "ES-EU_vox_es/2024-04-09_(6)",
           "ES-EU_vox_es/2024-04-14_(5)", "ES-EU_vox_es/2024-04-24_(6)", "ES-EU_santi_abascal/2024-05-10_(5)"}
KEEP_AS_WRITTEN = {"AFD", "VOX", "CDU", "CSU", "PSOE", "PVDA", "NVA", "EU", "UE", "NATO", "OTAN", "ONU"}
URLS = re.compile(r"https?://\S+|www\.\S+|@[\w.]+")
SENT_END = re.compile(r"[.!?…:;\"”»)\]]\s*$")

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
        english = google(text)  # retry with auto-detect
    return english

# capitals
def normal_case(line):
    words = [w for w in ("".join(c for c in tok if c.isalpha()) for tok in line.split()) if len(w) >= 2]
    if not words or sum(w.isupper() for w in words) / len(words) < 0.6:
        return line
    out, start = [], True
    for tok in re.split(r"(\s+)", line):
        alpha = "".join(c for c in tok if c.isalpha())
        if alpha.isupper() and alpha not in KEEP_AS_WRITTEN and not any(c.isdigit() for c in tok) \
                and any(c in "AEIOUY" for c in unicodedata.normalize("NFKD", alpha)):
            tok = tok.lower()
            if start:
                i = next(k for k, c in enumerate(tok) if c.isalpha())
                tok = tok[:i] + tok[i].upper() + tok[i + 1:]
        out.append(tok)
        if alpha:
            start = bool(re.search(r"[.!?…][\"'»”)\]]*$", tok))
    return "".join(out)

# captions
def join_broken_lines(par):
    out = []
    for line in (l.rstrip() for l in par.split("\n")):
        if out and out[-1].strip() and line.strip() and not SENT_END.search(out[-1]) \
                and re.match(r"[a-zà-ÿ]", line.strip()):
            out[-1] = out[-1] + " " + line.strip()
        else:
            out.append(line)
    return out

root = Path(sys.argv[1])
for path in sorted(root.glob("*/*_info.txt")):
    account, post = path.parent.name, path.name[:-len("_info.txt")]
    lang = "ca" if f"{account}/{post}" in CATALAN else LANG[account]
    if lang == "en":
        continue
    caption = path.read_text(encoding="utf-8").split(MARK)[0].rstrip()
    english, sent = [], 0
    for par in (p for p in re.split(r"\n\s*\n", caption) if p.strip()):
        if not any(c.isalpha() for c in URLS.sub(" ", par)):
            english.append(par.strip())  # emoji/links only
        else:
            english.append(to_english("\n".join(normal_case(l) for l in join_broken_lines(par)), lang).strip())
            sent += 1
    if sent:
        path.write_text(f"{caption}\n\n\n{MARK}\n" + "\n\n".join(english) + "\n", encoding="utf-8")
        print(f"{account}/{post}: {len(english)} paragraphs")
