#!/usr/bin/env bash
# ./01-download_instagram.sh DE_afd.bund | all | ACCOUNT START END
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
TABLE="$HERE/../../config/accounts.tsv"
CONFIG="$HERE/../../config/gallery-dl-config.json"
OUT="$HERE/../../data/00_raw"
WANT="${1:?Usage: $0 <account>|all [start end]}"

tail -n +2 "$TABLE" | while IFS=$'\t' read -r account url language start end election; do
  [[ "$WANT" == "all" || "$WANT" == "$account" ]] || continue
  start="${2:-$start}"; end="${3:-$end}"
  before=$(date -d "$end + 1 day" +%Y-%m-%d)
  echo "== $account  $start to $end  ($url)"
  gallery-dl --config "$CONFIG" \
    --date-after "$start" --date-before "$before" \
    -D "$OUT/$account" \
    "$url"
done
