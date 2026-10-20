# pipeline

scripts used to collect data - there may be some variability in reproducability depending on version changes or platform changes (e.g. instagram)
 
| Folders | |
|---|---|
| config/ | accounts.tsv (accounts, languages, windows) + gallery-dl settings |
| requirements/ | package lists, one per python env |
| scripts/comparative-countries/ | instagram, all 19 accounts |
| scripts/one-nation/ | PHON's other platforms + website |
| scripts/shared/ | dedup, both corpora |
| scripts/ai-detection/ | hive + sightengine |

## Instagram (in order)

| Scripts | |
|---|---|
| 01-download_instagram.sh | download images, videos, captions (gallery-dl) |
| 02-format_name_schema.py | rename to date_(n)_NN.ext |
| shared/deduplicate.py | flag duplicates |
| 03-ocr_images.py | on-image text (paddleocr) |
| 04-transcribe_audio.py | video speech (faster-whisper) |
| 05–07-translate_*.py | translate everything to english (google translate) |

## One Nation

| script | |
|---|---|
| 01–04 | fb photos, x posts, tiktok + youtube videos (gallery-dl, yt-dlp) |
| 05 | archived website (wayback-machine-downloader) |
| 06 | date website images from the wayback index |
| 07 | read content credentials for firefly use |

fb videos had no dates for when using downloaders, URLS had to be pulled directly by hand from Facebook and downloaded via jdownloader2

## AI Detection

hive.py + sightengine.py

## running

api keys as env vars

- GOOGLE_TRANSLATE_API_KEY - translation
- API_KEY - hive
- SIGHTENGINE_USER + SIGHTENGINE_SECRET - sightengine

separate python env per tool from requirements/ (3.12, 3.14 for gallery-dl)

ffmpeg, wayback-machine-downloader and videoduplicatefinder cli installed natively
