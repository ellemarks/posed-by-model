#!/usr/bin/env python3
# export GOOGLE_TRANSLATE_API_KEY
# python3 07-translate_subtitles.py ../../data/04_format
import os, re, sys, time, unicodedata
from pathlib import Path

import requests

SENT_END = re.compile(r'[.!?…]["\')\]]*\s*$')

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

# srt
def read_srt(path):
    cues = []
    for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8").strip()):
        lines = block.splitlines()
        if len(lines) >= 3 and "-->" in lines[1]:
            start, end = (s.strip() for s in lines[1].split("-->"))
            cues.append([start, end, " ".join(lines[2:]).strip()])
    return cues

def write_srt(path, cues):
    path.write_text("\n".join(f"{i}\n{a} --> {b}\n{t}\n" for i, (a, b, t) in enumerate(cues, 1)),
                    encoding="utf-8")

def sentences(cues):
    groups, cur = [], []
    for i, (_, _, text) in enumerate(cues):
        cur.append(i)
        joined = " ".join(cues[j][2] for j in cur)
        if SENT_END.search(text) or len(cur) >= 8 or len(joined) >= 600:
            groups.append(cur); cur = []
    return groups + ([cur] if cur else [])

def split_over(text, weights):
    # split back over cues
    words, n = text.split(), len(weights)
    if n == 1 or len(words) <= 1:
        return [text] + [""] * (n - 1)
    total_w, total_c = sum(weights), sum(len(w) + 1 for w in words)
    out, pos, cum = [], 0, 0.0
    for k in range(n - 1):
        cum += weights[k] / total_w
        take, run = pos, sum(len(w) + 1 for w in words[:pos])
        while take < len(words) - (n - 1 - k) and run < cum * total_c:
            run += len(words[take]) + 1; take += 1
        out.append(" ".join(words[pos:take])); pos = take
    return out + [" ".join(words[pos:])]

# files
root = Path(sys.argv[1])
for src in sorted(root.glob("*/*.*.srt")):
    stem, lang = src.name[:-len(".srt")].rsplit(".", 1)
    if lang == "en" or not re.fullmatch(r"[a-z]{2}", lang):
        continue
    cues = read_srt(src)
    out = []
    for group in sentences(cues):
        english = to_english(" ".join(cues[i][2] for i in group), lang)
        pieces = split_over(english, [max(1, len(cues[i][2])) for i in group])
        out += [[cues[i][0], cues[i][1], p] for i, p in zip(group, pieces) if p.strip()]
    write_srt(src.with_name(stem + ".srt"), out)
    print(f"{src.parent.name}/{stem}: {lang}, {len(cues)} cues")
