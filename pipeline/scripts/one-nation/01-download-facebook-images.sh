#!/usr/bin/env bash
# ./facebook-dl.sh <url>
# https://www.facebook.com/PaulineHansonAu/
# https://www.facebook.com/OneNationParty/

gallery-dl \
  --filename "{date}_{author[name]}" \
  --user-agent "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36" \
  --cookies-from-browser chrome \
  --date-before "2025-05-04" \
  --date-after  "2025-01-03" \
  \
  -o "author-followups=false" \
  -o "include=photos" \
  -o "loop=true" \
  -o "videos=ytdl" \
  \
  "$@"
