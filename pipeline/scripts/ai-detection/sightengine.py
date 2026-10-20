#!/usr/bin/env python3
# export SIGHTENGINE_USER
# export SIGHTENGINE_SECRET
# python3 sightengine.py images.txt
import csv, hashlib, os, sys, time
from pathlib import Path

import requests

USER, SECRET = os.environ["SIGHTENGINE_USER"], os.environ["SIGHTENGINE_SECRET"]
OUT = Path("scores.tsv")

done, listed = {}, set()
if OUT.exists():
    for r in csv.DictReader(open(OUT, encoding="utf-8"), delimiter="\t"):
        done[r["sha256"]] = r["ai_generated"]; listed.add(r["path"])
new = not OUT.exists()
with open(OUT, "a", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, delimiter="\t", lineterminator="\n")
    if new:
        w.writerow(["path", "sha256", "ai_generated"])
    for line in open(sys.argv[1], encoding="utf-8"):
        path = Path(line.strip())
        if not line.strip() or str(path) in listed:
            continue
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        if sha not in done:
            with open(path, "rb") as media:
                r = requests.post("https://api.sightengine.com/1.0/check.json", files={"media": media},
                                  data={"models": "genai", "api_user": USER, "api_secret": SECRET}, timeout=60)
            r.raise_for_status()
            reply = r.json()
            if reply.get("status") != "success":
                sys.exit(f"{path}: {reply}")
            done[sha] = reply["type"]["ai_generated"]
            time.sleep(0.5)
        w.writerow([str(path), sha, done[sha]]); listed.add(str(path))
        print(f"{path}: {done[sha]}")
