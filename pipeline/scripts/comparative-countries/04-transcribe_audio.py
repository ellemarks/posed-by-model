#!/usr/bin/env python3
# python3 04-transcribe_audio.py ../../data/04_format [--only account/stem] [--model] [--language]
import argparse, csv, ctypes, glob, os, subprocess
from pathlib import Path


def load_cuda_libraries():
    # load pip cuda libs
    try:
        import nvidia
    except ImportError:
        return
    for base in nvidia.__path__:
        for pattern in ("cublas/lib/libcublasLt.so*", "cublas/lib/libcublas.so*",
                        "cudnn/lib/libcudnn_*.so*", "cudnn/lib/libcudnn.so*"):
            for lib in sorted(glob.glob(os.path.join(base, pattern))):
                try:
                    ctypes.CDLL(lib, mode=ctypes.RTLD_GLOBAL)
                except OSError:
                    pass


load_cuda_libraries()
from faster_whisper import WhisperModel, decode_audio

VIDEOS = {".mp4", ".mov", ".webm", ".mkv"}
TABLE = Path(__file__).resolve().parents[2] / "config" / "accounts.tsv"
LANG = {r["account"]: r["language"] for r in csv.DictReader(open(TABLE, encoding="utf-8"), delimiter="\t")}
DECODE = dict(beam_size=5, best_of=5, temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
              compression_ratio_threshold=2.4, log_prob_threshold=-1.0,
              no_speech_threshold=1.0, condition_on_previous_text=False,
              word_timestamps=True)


def stamp(t):
    ms = int(round(max(t, 0) * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def write_srt(path, cues):
    path.write_text("\n".join(f"{i}\n{stamp(a)} --> {stamp(b)}\n{text.strip()}\n"
                              for i, (a, b, text) in enumerate(cues, 1)), encoding="utf-8")


def duration(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(video)], capture_output=True, text=True).stdout
    return float(out.strip() or 0)


ap = argparse.ArgumentParser()
ap.add_argument("root")
ap.add_argument("--model", default="large-v3")
ap.add_argument("--language", help="override the account's language")
ap.add_argument("--only", nargs="*", help="account/stem of the videos to (re)do")
args = ap.parse_args()

root = Path(args.root)
model = WhisperModel(args.model, device="cuda", compute_type="float16")
for video in sorted(p for p in root.glob("*/*") if p.suffix.lower() in VIDEOS):
    account, stem = video.parent.name, video.stem
    if args.only and f"{account}/{stem}" not in args.only:
        continue
    lang = args.language or LANG[account]
    out = video.with_name(stem + (".srt" if lang == "en" else f".{lang}.srt"))
    if not args.only and (out.exists() or video.with_suffix(".srt").exists()):
        continue
    try:
        audio = decode_audio(str(video), sampling_rate=16000)
    except Exception:  # no audio
        write_srt(video.with_suffix(".srt"), [(0, duration(video), "[no audio stream]")])
        print(f"{account}/{stem}: no audio stream, placeholder written")
        continue
    segments, _ = model.transcribe(audio, language=lang, task="transcribe", **DECODE)
    cues = [(s.start, s.end, s.text) for s in segments]
    write_srt(out, cues)
    print(f"{account}/{stem}: {lang}, {len(cues)} cues")
