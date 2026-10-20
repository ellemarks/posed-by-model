#!/usr/bin/env bash
# ./twitter-dl.sh <url>
# https://x.com/OneNationAus
# https://x.com/PaulineHansonOz

gallery-dl \
  --filename "{date}_{author[name]}" \
  --user-agent "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36" \
  --cookies-from-browser chrome \
  --date-before "2025-05-04" \
  --date-after  "2025-01-03" \
  \
  -o "text-tweets=true" \
  -o "retweets=true" \
  \
  --postprocessor "metadata" \
  -o "postprocessor.metadata.event=post" \
  -o "postprocessor.metadata.filename={date}_{author[name]}.txt" \
  -o "postprocessor.metadata.mode=custom" \
  -o "postprocessor.metadata.format={content|description}\n" \
  \
  "$@"
