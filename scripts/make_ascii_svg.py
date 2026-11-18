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
CONTRAST = 2.0
GAMMA = 1.15
WHITE_FLOOR = 18

ASCII_CHARS = "@%#*+=-:. "
# =========================


def brightness_to_ascii(val):
    idx = int(val / 255 * (len(ASCII_CHARS) - 1))
    return ASCII_CHARS[idx]


def generate_default_cyber_portrait():
    """Generates a stylish cyberpunk developer portrait if no image is provided."""
    img = Image.new("RGB", (720, 780), color=(12, 16, 26))
    draw = ImageDraw.Draw(img)

    # Torso / hoodie
    draw.polygon([(70, 780), (190, 520), (530, 520), (650, 780)], fill=(220, 225, 235))
    # Collar / neck
    draw.rectangle([(270, 460), (450, 540)], fill=(240, 245, 255))
    # Head contour
    draw.ellipse([(220, 160), (500, 480)], fill=(255, 255, 255))
    # Modern cyber hair
    draw.polygon(
        [
            (190, 170),
            (240, 90),
            (360, 80),
            (480, 95),
            (530, 170),
            (510, 290),
            (470, 250),
            (360, 230),
            (250, 250),
            (210, 290),
        ],
        fill=(30, 35, 50),
    )
    # Headset / Headphones
    draw.arc([(200, 140), (520, 340)], start=180, end=0, fill=(35, 40, 55), width=24)
    draw.rounded_rectangle([(180, 260), (225, 380)], radius=15, fill=(35, 40, 55))
    draw.rounded_rectangle([(495, 260), (540, 380)], radius=15, fill=(35, 40, 55))

    # Neural Visor / Glasses
    draw.polygon([(250, 290), (470, 290), (450, 345), (270, 345)], fill=(20, 25, 38))
    draw.line([(260, 318), (460, 318)], fill=(255, 255, 255), width=4)

    # Jaw & smile accent
    draw.polygon([(345, 370), (375, 370), (360, 410)], fill=(210, 215, 225))
    draw.line([(325, 440), (395, 440)], fill=(170, 175, 190), width=4)

    return img


def image_to_ascii(img_or_path, width=84):
    if isinstance(img_or_path, str):
        if not os.path.exists(img_or_path):
            print(f"[!] Warning: Image {img_or_path} not found. Using default cyber portrait.")
            img = generate_default_cyber_portrait()
        else:
            print(f"[*] Processing user photo: {img_or_path}")
            img = Image.open(img_or_path)
    else:
        img = img_or_path

    # Convert to grayscale
    img = img.convert("L")
    img = ImageOps.autocontrast(img, cutoff=1)
    img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=150, threshold=2))

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
    height = int(width * aspect_ratio * 0.58)
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
    height = 905

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
        '      <stop offset="50%" stop-color="#3b82f6" stop-opacity="0.25"/>',
        '      <stop offset="100%" stop-color="#00ff9d" stop-opacity="0.4"/>',
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
        f'  <text x="{width / 2:.1f}" y="20" fill="#94a3b8" font-size="12" text-anchor="middle">supriyo@github: ~$ ./portrait.sh</text>',
    ]

    for row_idx, row in enumerate(ascii_grid):
        y = 39 + row_idx * 13
        if y > 840:
            break
        clip_id = f"r{row_idx}"
        delay = row_idx * 0.04
        svg.extend([
            f'  <clipPath id="{clip_id}"><rect x="20" y="{y - 11}" height="15" width="0"><animate attributeName="width" from="0" to="800" begin="{delay:.2f}s" dur="0.10s" fill="freeze"/></rect></clipPath>',
            f'  <g clip-path="url(#{clip_id})"><text xml:space="preserve" x="20" y="{y}" fill="#cbd5e1" font-size="12.9" textLength="800" lengthAdjust="spacing">{escape_xml(row)}</text></g>',
            f'  <rect y="{y - 11}" width="8" height="13" fill="#00ff9d" opacity="0"><animate attributeName="x" from="20" to="820" begin="{delay:.2f}s" dur="0.10s" fill="freeze"/><set attributeName="opacity" to=".85" begin="{delay:.2f}s"/><set attributeName="opacity" to="0" begin="{delay + 0.10:.2f}s"/></rect>',
        ])

    svg.extend([
        '  <line x1="0" y1="862" x2="840" y2="862" stroke="#1e293b"/>',
        '  <text x="20" y="882" fill="#64748b" font-size="13">supriyo@github:~$ whoami <tspan fill="#00ff9d" font-weight="600">Supriyo Hara</tspan> <tspan fill="#38bdf8">[AI/CV Developer]</tspan></text>',
        '</svg>',
    ])

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))

    print(f"[+] Created Animated ASCII Portrait SVG: {output_file}")


if __name__ == "__main__":
    img_input = sys.argv[1] if len(sys.argv) > 1 else None
    out_file = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT_SVG

    if img_input and os.path.exists(img_input):
        grid = image_to_ascii(img_input, WIDTH)
    else:
        grid = image_to_ascii(generate_default_cyber_portrait(), WIDTH)

    create_animated_svg(grid, out_file)
