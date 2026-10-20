import os, sys, time, json, requests


# export API_KEY
# python3 hive.py FOLDER_OR_IMAGE
DELAY = 1
API_KEY = os.environ["API_KEY"]

paths = []
for arg in sys.argv[1:]:
    if os.path.isdir(arg):
        paths += [os.path.join(arg, name) for name in sorted(os.listdir(arg))]
    elif os.path.isfile(arg):
        paths.append(arg)
    else:
        print(f"not found: {arg}")
        sys.exit(1)

for path in paths:
    filename = os.path.basename(path)
    if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        continue
    json_path = f"{os.path.splitext(path)[0]}.json"
    if os.path.exists(json_path):
        print(f"skipping {filename}")
        continue
    with open(path, "rb") as f:
        r = requests.post(
            "https://api.thehive.ai/api/v3/hive/ai-generated-and-deepfake-content-detection",
            headers={"authorization": f"Bearer {API_KEY}"},
            files={"media": f},
            data={"processing_mode": "sync_with_fallback"}
        )
    if r.status_code != 200:
        print(f"Error {r.status_code} on {filename} exiting without writing JSON")
        sys.exit(1)
    json.dump(r.json(), open(json_path, "w"), indent=2)
    print(filename, r.status_code)
    time.sleep(DELAY)
