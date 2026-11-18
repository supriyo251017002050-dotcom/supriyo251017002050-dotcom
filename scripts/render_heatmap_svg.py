#!/usr/bin/env python3
"""
render_heatmap_svg.py - Render an animated terminal-themed GitHub contribution graph SVG.
Outputs: contrib-heatmap.svg
"""

import json
import sys
from datetime import datetime, timedelta

# ===== CONFIGURATION =====
INPUT_FILE = "contributions.json"
OUTPUT_FILE = "contrib-heatmap.svg"

CELL_SIZE = 12
CELL_GAP = 3
WEEKS_TO_SHOW = 53
# =========================


def load_contributions(input_path):
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[!] Error: {input_path} not found. Running fetch_contributions first...")
        from fetch_contributions import fetch_contributions, save_json
        data = fetch_contributions("supriyo251017002050-dotcom")
        save_json(data, input_path)
        return data


def get_level_color(count):
    if count == 0:
        return "#121826"
    elif count < 3:
        return "#0284c7"
    elif count < 6:
        return "#06b6d4"
    elif count < 9:
        return "#10b981"
    else:
        return "#00ff9d"


def create_heatmap_svg(data, output_path=OUTPUT_FILE):
    contributions = {c["date"]: c["count"] for c in data.get("contributions", [])}

    width = 869
    height = 265
    today = datetime.now()
    # Align to Saturday of the current week for a standard GitHub grid
    days_since_saturday = (today.weekday() + 2) % 7
    end_date = today - timedelta(days=days_since_saturday)
    start_date = end_date - timedelta(days=WEEKS_TO_SHOW * 7 - 1)

    day_labels = ["Mon", "Wed", "Fri"]
    username = data.get("username", "supriyo")

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        '  <style>',
        '    @keyframes cellFade {',
        '      0% { opacity: 0; transform: scale(0.65) translateY(-4px); }',
        '      100% { opacity: 1; transform: scale(1) translateY(0); }',
        '    }',
        '    .cell { opacity: 0; animation: cellFade 0.45s cubic-bezier(0.2, 0.8, 0.2, 1) both; transform-origin: center; }',
        '    .cell:hover { stroke: #00f0ff; stroke-width: 1.5; }',
        '  </style>',
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
        f'  <line x1="0" y1="32" x2="{width}" y2="32" stroke="#1e293b" stroke-width="1"/>',
        '',
        '  <!-- Window Buttons -->',
        '  <circle cx="22" cy="16" r="5" fill="#ff5f56"/>',
        '  <circle cx="38" cy="16" r="5" fill="#ffbd2e"/>',
        '  <circle cx="54" cy="16" r="5" fill="#27c93f"/>',
        f'  <text x="{width / 2:.1f}" y="20" fill="#94a3b8" font-size="12" text-anchor="middle">{username}@github: ~/contributions --graph</text>',
    ]

    # Month labels calculated along the 53 weeks
    last_month = None
    for week in range(WEEKS_TO_SHOW):
        current_date = start_date + timedelta(days=week * 7)
        month_name = current_date.strftime("%b")
        if month_name != last_month and current_date.day <= 14:
            x = 52 + week * (CELL_SIZE + CELL_GAP)
            svg.append(f'  <text x="{x}" y="47" fill="#64748b" font-size="10">{month_name}</text>')
            last_month = month_name

    # Day labels
    for i, day in enumerate(day_labels):
        y = 75.5 + i * 30
        svg.append(f'  <text x="22" y="{y}" fill="#64748b" font-size="9">{day}</text>')

    # Contribution cells
    total_cells = WEEKS_TO_SHOW * 7
    cell_idx = 0
    for week in range(WEEKS_TO_SHOW):
        for day in range(7):
            current_date = start_date + timedelta(days=week * 7 + day)
            date_str = current_date.strftime("%Y-%m-%d")
            x = 52 + week * (CELL_SIZE + CELL_GAP)
            y = 62 + day * (CELL_SIZE + CELL_GAP)
            count = contributions.get(date_str, 0)
            color = get_level_color(count)
            delay = (cell_idx / total_cells) * 0.95

            svg.append(
                f'  <rect class="cell" x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" rx="2.5" '
                f'fill="{color}" stroke="#1e293b" stroke-width="0.5" style="animation-delay:{delay:.3f}s">'
                f'<title>{date_str}: {count} contribution{"s" if count != 1 else ""}</title></rect>'
            )
            cell_idx += 1

    # Legend & Stats footer
    total = data.get("total_contributions", 0)
    current_streak = data.get("current_streak", 0)
    longest_streak = data.get("longest_streak", 0)

    legend_x = 52
    legend_y = height - 24
    svg.append(f'  <text x="{legend_x}" y="{legend_y}" fill="#64748b" font-size="10">Less</text>')
    colors = ["#121826", "#0284c7", "#06b6d4", "#10b981", "#00ff9d"]
    for i, color in enumerate(colors):
        x = legend_x + 32 + i * (CELL_SIZE + 3)
        svg.append(f'  <rect x="{x}" y="{legend_y - 9}" width="{CELL_SIZE}" height="{CELL_SIZE}" rx="2.5" fill="{color}" stroke="#1e293b" stroke-width="0.5"/>')
    svg.append(f'  <text x="{legend_x + 32 + len(colors) * (CELL_SIZE + 3) + 6}" y="{legend_y}" fill="#64748b" font-size="10">More</text>')

    # Stats
    svg.append(f'  <text x="{legend_x + 220}" y="{legend_y}" fill="#38bdf8" font-size="11" font-weight="600">Total: <tspan fill="#f8fafc">{total}</tspan> contributions</text>')
    svg.append(f'  <text x="{legend_x + 420}" y="{legend_y}" fill="#64748b" font-size="11">Current Streak: <tspan fill="#00ff9d">{current_streak} days</tspan></text>')
    svg.append(f'  <text x="{legend_x + 590}" y="{legend_y}" fill="#64748b" font-size="11">Longest Streak: <tspan fill="#38bdf8">{longest_streak} days</tspan></text>')

    svg.append('</svg>')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))

    print(f"[+] Rendered heatmap SVG to: {output_path}")


if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else INPUT_FILE
    out = sys.argv[2] if len(sys.argv) > 2 else OUTPUT_FILE
    data = load_contributions(inp)
    create_heatmap_svg(data, out)
