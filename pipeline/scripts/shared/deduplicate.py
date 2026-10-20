#!/usr/bin/env python3
# python3 deduplicate.py ../../data/04_format
import argparse, csv, shutil, subprocess, tempfile
from pathlib import Path

IMAGES = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def groups(pairs):
    # merge pairs into groups
    parent = {}
    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for a, b in pairs:
        parent[find(a)] = find(b)
    out = {}
    for x in parent:
        out.setdefault(find(x), []).append(x)
    return [sorted(g) for g in out.values() if len(g) > 1]


ap = argparse.ArgumentParser()
ap.add_argument("root")
ap.add_argument("--vdf-cli", default=shutil.which("vdf-cli")
args = ap.parse_args()
root = Path(args.root).resolve()
rows = []

# images
from imagededup.methods import PHash
phash = PHash()
files = sorted(p for p in root.rglob("*") if p.suffix.lower() in IMAGES)
hashes = {str(p.relative_to(root)): phash.encode_image(image_file=str(p)) for p in files}
found = phash.find_duplicates(encoding_map=hashes, max_distance_threshold=0)
for g in groups((a, b) for a, matches in found.items() for b in matches):
    rows += [("image", copy, g[0], "phash 0") for copy in g[1:]]

# videos
if not args.vdf_cli:
    print("vdf-cli not found: videos not checked")
else:
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "vdf.csv"
        subprocess.run([args.vdf_cli, "scan-and-compare", "--include", str(root),
                        "--format", "csv", "--output", str(report)], check=True)
        by_group = {}
        for r in csv.DictReader(open(report, encoding="utf-8-sig")):
            if str(r.get("IsImage", "False")).lower() != "true":
                by_group.setdefault(r["GroupId"], []).append(str(Path(r["Path"]).resolve().relative_to(root)))
    for g in (sorted(v) for v in by_group.values() if len(v) > 1):
        rows += [("video", copy, g[0], "vdf") for copy in g[1:]]

with open(root / "duplicates.tsv", "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, delimiter="\t", lineterminator="\n")
    w.writerow(["kind", "file", "duplicate_of", "method"])
    w.writerows(rows)
print(f"{len(files)} images checked; {len(rows)} duplicates flagged -> {root / 'duplicates.tsv'}")
