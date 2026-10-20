#!/usr/bin/env bash
# ./05-download-party_website.sh

WMD=~/.local/share/gem/ruby/3.4.0/bin/wayback_machine_downloader
ONLY="/\.(jpg|jpeg|png|gif|webp|svg|ico|mp4|mov|avi|wmv|mkv|webm|flv|m4v|mp3|wav|ogg)$/i"

for url in \
  "https://www.onenation.org.au/*" \
  "https://assets.nationbuilder.com/onenation/*" \
  "https://d3n8a8pro7vhmx.cloudfront.net/onenation/*" \
  "https://www.senatorhanson.com.au/*" \
  "https://i0.wp.com/www.senatorhanson.com.au/*"
do
  domain=$(echo "$url" | sed 's|https://||;s|/\*||')
  $WMD "$url" \
    --only "$ONLY" \
    --concurrency 5 \
    --directory "./${domain}/"
done
