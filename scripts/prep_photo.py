#!/usr/bin/env python3
"""
prep_photo.py - Contrast enhancement and preprocessing for custom photos
Usage:
    python scripts/prep_photo.py <input_image> <output_image>
"""

import sys
import cv2
import numpy as np
from PIL import Image

CLIP_LIMIT = 3.0
TILE_GRID_SIZE = (8, 8)


def prep_photo(input_path, output_path):
    print(f"[*] Preprocessing photo: {input_path}")
    img = Image.open(input_path)

    # Convert to RGB if needed
    if img.mode != "RGB":
        img = img.convert("RGB")

    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    # Convert to LAB for luminance-only CLAHE
    lab = cv2.cvtColor(img_cv, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=CLIP_LIMIT, tileGridSize=TILE_GRID_SIZE)
    l_enhanced = clahe.apply(l)

    enhanced_lab = cv2.merge([l_enhanced, a, b])
    enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    enhanced_rgb = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)

    result = Image.fromarray(enhanced_rgb)
    result.save(output_path)
    print(f"[+] Enhanced image saved to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/prep_photo.py <input_image> <output_image>")
        sys.exit(1)
    prep_photo(sys.argv[1], sys.argv[2])
