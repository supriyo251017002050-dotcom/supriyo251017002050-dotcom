#!/usr/bin/env python3
"""
make_ascii_svg.py - Convert an image or portrait into an animated ASCII terminal SVG.
Usage:
    python scripts/make_ascii_svg.py [image_path] [output_svg]
Outputs: avi-ascii.svg
"""

import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

# ===== CONFIGURATION =====
DEFAULT_OUTPUT_SVG = "avi-ascii.svg"
WIDTH = 84
CONTRAST = 2.2
GAMMA = 1.15
WHITE_FLOOR = 15

ASCII_CHARS = "@%#*+=-:. "
# =========================


def brightness_to_ascii(val):
    idx = int(val / 255 * (len(ASCII_CHARS) - 1))
    return ASCII_CHARS[idx]


def image_to_ascii(img_or_path, width=84):
    if isinstance(img_or_path, str):
        if not os.path.exists(img_or_path):
            print(f"[!] File not found: {img_or_path}")
            sys.exit(1)
        print(f"[*] Processing image: {img_or_path}")
        img = Image.open(img_or_path)
    else:
        img = img_or_path

    # If landscape (aspect > 1.3), center-crop to focus on the core subject
    w, h = img.size
    if w / h > 1.35:
        print("[*] Landscape image detected: applying focus crop to core subject")
        crop_w = int(h * 1.22)
        left = max(0, (w - crop_w) // 2)
        img = img.crop((left, 0, left + crop_w, h))

    # Convert to grayscale
    img = img.convert("L")
    img = ImageOps.autocontrast(img, cutoff=2)
    img = img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=180, threshold=2))

    if CONTRAST != 1.0:
        img = ImageEnhance.Contrast(img).enhance(CONTRAST)

    if GAMMA != 1.0:
        arr = np.array(img).astype(float)
        arr = 255 * np.power(arr / 255, 1 / GAMMA)
        img = Image.fromarray(arr.astype(np.uint8))

    if WHITE_FLOOR > 0:
        arr = np.array(img)
        arr = np.maximum(arr, WHITE_FLOOR)
        img = Image.fromarray(arr)

    aspect_ratio = img.height / img.width
    height = int(width * aspect_ratio * 0.72)
    img = img.resize((width, height), Image.Resampling.LANCZOS)

    pixels = np.array(img)
    return ["".join(brightness_to_ascii(pixel) for pixel in row) for row in pixels]


def escape_xml(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def create_animated_svg(ascii_grid, output_file=DEFAULT_OUTPUT_SVG):
    width = 840
    row_height = 13
    start_y = 39
    num_rows = len(ascii_grid)
    content_bottom = start_y + num_rows * row_height

    footer_line_y = content_bottom + 16
    footer_text_y = content_bottom + 36
    height = content_bottom + 52

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace">',
        '  <defs>',
        '    <linearGradient id="termBg" x1="0" y1="0" x2="0" y2="1">',
        '      <stop offset="0%" stop-color="#0a0f1d"/>',
        '      <stop offset="100%" stop-color="#050811"/>',
        '    </linearGradient>',
        '    <linearGradient id="borderGlow" x1="0" y1="0" x2="1" y2="1">',
        '      <stop offset="0%" stop-color="#00f0ff" stop-opacity="0.5"/>',
        '      <stop offset="50%" stop-color="#a855f7" stop-opacity="0.3"/>',
        '      <stop offset="100%" stop-color="#00ff9d" stop-opacity="0.4"/>',
        '    </linearGradient>',
        '    <linearGradient id="puzzleGrad" x1="0" y1="0" x2="1" y2="1">',
        '      <stop offset="0%" stop-color="#38bdf8"/>',
        '      <stop offset="35%" stop-color="#a78bfa"/>',
        '      <stop offset="70%" stop-color="#f472b6"/>',
        '      <stop offset="100%" stop-color="#34d399"/>',
        '    </linearGradient>',
        '  </defs>',
        '',
        '  <!-- Terminal Chassis -->',
        f'  <rect width="{width}" height="{height}" rx="12" fill="url(#termBg)"/>',
        f'  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="none" stroke="url(#borderGlow)" stroke-width="1"/>',
        f'  <line x1="0" y1="32" x2="{width}" y2="32" stroke="#1e293b"/>',
        '',
        '  <!-- Window Buttons -->',
        '  <circle cx="20" cy="16" r="5" fill="#ff5f56"/>',
        '  <circle cx="36" cy="16" r="5" fill="#ffbd2e"/>',
        '  <circle cx="52" cy="16" r="5" fill="#27c93f"/>',
        f'  <text x="{width / 2:.1f}" y="20" fill="#94a3b8" font-size="12" text-anchor="middle">supriyo@github: ~$ ./solve_puzzle.sh</text>',
    ]

    for row_idx, row in enumerate(ascii_grid):
        y = start_y + row_idx * row_height
        clip_id = f"r{row_idx}"
        delay = row_idx * 0.035
        svg.extend([
            f'  <clipPath id="{clip_id}"><rect x="20" y="{y - 11}" height="15" width="0"><animate attributeName="width" from="0" to="800" begin="{delay:.2f}s" dur="0.09s" fill="freeze"/></rect></clipPath>',
            f'  <g clip-path="url(#{clip_id})"><text xml:space="preserve" x="20" y="{y}" fill="url(#puzzleGrad)" font-size="12.9" textLength="800" lengthAdjust="spacing">{escape_xml(row)}</text></g>',
            f'  <rect y="{y - 11}" width="8" height="13" fill="#38bdf8" opacity="0"><animate attributeName="x" from="20" to="820" begin="{delay:.2f}s" dur="0.09s" fill="freeze"/><set attributeName="opacity" to=".85" begin="{delay:.2f}s"/><set attributeName="opacity" to="0" begin="{delay + 0.09:.2f}s"/></rect>',
        ])

    svg.extend([
        f'  <line x1="0" y1="{footer_line_y}" x2="{width}" y2="{footer_line_y}" stroke="#1e293b"/>',
        f'  <text x="20" y="{footer_text_y}" fill="#64748b" font-size="13">supriyo@github:~$ whoami <tspan fill="#34d399" font-weight="600">Supriyo Hara</tspan> <tspan fill="#38bdf8">[AI &amp; Problem Solver]</tspan></text>',
        '</svg>',
    ])

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))

    print(f"[+] Created Animated ASCII SVG: {output_file} ({width}x{height}px, {num_rows} rows)")


if __name__ == "__main__":
    img_input = sys.argv[1] if len(sys.argv) > 1 else None
    out_file = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT_SVG

    if not img_input:
        print("[!] No input image provided.")
        sys.exit(1)

    grid = image_to_ascii(img_input, WIDTH)
    create_animated_svg(grid, out_file)
