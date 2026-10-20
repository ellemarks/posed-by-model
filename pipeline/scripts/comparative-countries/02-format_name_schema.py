#!/usr/bin/env python3
# Aided by Claude Opus 5
# regex is evil
import re, os, sys
from collections import defaultdict
from pathlib import Path

dir = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
pat = re.compile(r'^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})(?:_(\d+))?(?= |\.|_)')

# Group files by date, then by time within each date
by_date = defaultdict(lambda: defaultdict(list))
for f in sorted(dir.iterdir()):
    if m := pat.match(f.name):
        by_date[m.group(1)][m.group(2)].append(f)

for date, times in by_date.items():
    for i, (time, files) in enumerate(sorted(times.items())):
        group = f"_({i+1})" if len(times) > 1 else ""
        for f in files:
            m = pat.match(f.name)
            ext = f.suffix
            if m.group(3):  # has _N index
                new = f"{date}{group}_{int(m.group(3)):02d}{ext}"
            else:            # info .txt
                new = f"{date}{group}_info.txt"
            f.rename(dir / new)
            print(f"{f.name} -> {new}")

