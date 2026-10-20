#!/usr/bin/env python3
# python3 03-ocr_images.py ../../data/04_format
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from paddleocr import PaddleOCR

IMAGES = {".jpg", ".jpeg", ".png", ".webp"}
ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv6_medium_det",
    text_recognition_model_name="PP-OCRv6_medium_rec",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=True,
)

root = Path(sys.argv[1])
for image in sorted(p for p in root.glob("*/*") if p.suffix.lower() in IMAGES):
    out = image.with_suffix(".ocr.txt")
    if out.exists():
        continue
    bgr = np.array(Image.open(image).convert("RGB"))[:, :, ::-1].copy()
    result = ocr.predict(bgr)[0]
    lines = [str(t) for t in result["rec_texts"]]
    out.write_text("".join(line + "\n" for line in lines), encoding="utf-8")
    print(f"{image.relative_to(root)}: {len(lines)} lines")
