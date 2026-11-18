#!/usr/bin/env python3
"""
make_info_card.py - Generate a terminal-style neofetch spec card SVG
Outputs: info-card.svg
"""

import sys

# ===== CONFIGURATION =====
NAME = "Supriyo Hara"
SUBTITLE = "Data Science & AI • Problem Solving • Computer Vision"

ROWS = [
    ("Education", "BCA in Data Science & AI"),
    ("University", "Techno India University, Kolkata"),
    ("Focus", "Complex Problem Solving • Computer Vision • AI"),
    ("Languages", "Python • C++ • JavaScript • TypeScript • SQL"),
    ("Stack", "PyTorch • OpenCV • TensorFlow • React • Algorithms"),
    ("Highlights", "ClimateGuard AI • FIFA Crowd Vision • Memora VR"),
]

PROGRESS = [
    ("Logic & Algorithms", 96),
    ("Python / AI", 94),
    ("Computer Vision", 88),
    ("Full-Stack & APIs", 82),
]

HOST = "github.com/supriyo251017002050-dotcom"
OUTPUT_FILE = "info-card.svg"

W = 490
H = 390
PADDING = 22
# =========================


def escape_xml(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def build_reveal_text(text, x, y, fill, size, weight, begin, font_family=None):
    font_attr = f' font-family="{font_family}"' if font_family else ""
    parts = [f'<text x="{x}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" fill="{fill}"{font_attr}>']
    for idx, ch in enumerate(text):
        ch_text = escape_xml(ch)
        if ch == " ":
            ch_text = "&#160;"
        start = begin + idx * 0.045
        parts.append(
            f'<tspan opacity="0"><animate attributeName="opacity" from="0" to="1" '
            f'begin="{start:.2f}s" dur="0.01s" fill="freeze"/>{ch_text}</tspan>'
        )
    parts.append("</text>")
    return parts


def create_info_card(output_path=OUTPUT_FILE):
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
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
        '    <linearGradient id="barGrad" x1="0" y1="0" x2="1" y2="0">',
        '      <stop offset="0%" stop-color="#06b6d4"/>',
        '      <stop offset="50%" stop-color="#818cf8"/>',
        '      <stop offset="100%" stop-color="#00ff9d"/>',
        '    </linearGradient>',
        '  </defs>',
        '',
        '  <!-- Terminal Chassis -->',
        f'  <rect width="{W}" height="{H}" rx="12" fill="url(#termBg)"/>',
        f'  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="url(#borderGlow)" stroke-width="1"/>',
        f'  <line x1="0" y1="32" x2="{W}" y2="32" stroke="#1e293b"/>',
        '',
        '  <!-- Window Buttons -->',
        '  <circle cx="20" cy="16" r="5" fill="#ff5f56"/>',
        '  <circle cx="36" cy="16" r="5" fill="#ffbd2e"/>',
        '  <circle cx="52" cy="16" r="5" fill="#27c93f"/>',
        f'  <text x="{W / 2:.1f}" y="20" fill="#94a3b8" font-size="12" text-anchor="middle">supriyo@github: ~$ neofetch --specs</text>',
    ]

    svg.append('  <g transform="translate(0, 4)">')
    # Animated Typewriter Title
    svg.extend(build_reveal_text(NAME, PADDING, 58.0, "#00ff9d", 22, 800, 0.05))
    svg.extend(build_reveal_text(SUBTITLE, PADDING, 80.0, "#38bdf8", 12, 500, 0.45))

    # Spec rows
    y = 106
    for idx, (label, value) in enumerate(ROWS):
        svg.append(f'  <text x="{PADDING}" y="{y:.1f}" font-size="12" font-weight="500">')
        svg.append(f'    <tspan fill="#00f0ff" font-weight="600">{escape_xml(label.lower())}: </tspan>')
        svg.append(f'    <tspan fill="#e2e8f0">{escape_xml(value)}</tspan>')
        svg.append('  </text>')
        y += 20

    # Skills progress section
    progress_y = y + 10
    svg.append(
        f'  <text x="{PADDING}" y="{progress_y:.1f}" font-size="12" font-weight="700" fill="#f8fafc">skills</text>'
    )
    for i, (name, pct) in enumerate(PROGRESS):
        bar_y = progress_y + 17 + i * 18
        bar_width = int(140 * pct / 100)
        svg.extend([
            f'  <text x="{PADDING}" y="{bar_y:.1f}" font-size="11" fill="#94a3b8">{escape_xml(name)}</text>',
            f'  <rect x="{PADDING + 120}" y="{bar_y - 8:.1f}" width="140" height="7" rx="3.5" fill="#0f172a" stroke="#1e293b" stroke-width="1"/>',
            f'  <rect x="{PADDING + 120}" y="{bar_y - 8:.1f}" width="{bar_width}" height="7" rx="3.5" fill="url(#barGrad)"/>',
            f'  <text x="{PADDING + 270}" y="{bar_y:.1f}" font-size="11" fill="#38bdf8" font-weight="600">{pct}%</text>',
        ])

    # Watermark Footer
    svg.append(f'  <text x="{PADDING}" y="{H - 18:.1f}" fill="#64748b" font-size="11">{escape_xml(HOST)}</text>')
    svg.append('  </g>')
    svg.append('</svg>')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))

    print(f"[+] Created Info Card SVG: {output_path}")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else OUTPUT_FILE
    create_info_card(out)
