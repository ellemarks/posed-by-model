#!/usr/bin/env bash
set -euo pipefail
# run with ./youtube-all.sh <ACCOUNT_URL>
# https://www.youtube.com/@OnenationAus
# https://www.youtube.com/@PaulineHansonsPleaseExplain
 
ACCOUNT_URL="${1:?Usage: $0 <ACCOUNT_URL>}"
USERNAME=$(echo "$ACCOUNT_URL" | grep -oP '(?<=@)[^/?]+')
OUTPUT_DIR="../../data/one-nation/raw/youtube/${USERNAME}"
mkdir -p "$OUTPUT_DIR"
 
yt-dlp \
  --cookies-from-browser firefox \
  --dateafter  20250103 \
  --datebefore 20250504 \
  --output "$OUTPUT_DIR/%(upload_date)s - %(title)s [%(id)s].%(ext)s" \
  --write-info-json \
  --write-description \
  --format "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
  --retries 10 \
  --fragment-retries 10 \
  --sleep-requests 2 \
  --sleep-interval 3 \
  --max-sleep-interval 8 \
  --ignore-errors \
  --no-abort-on-error \
  "$ACCOUNT_URL"
 
# Note even though this script is marked as all (i.e. video/image), both youtube pages only contained videos
