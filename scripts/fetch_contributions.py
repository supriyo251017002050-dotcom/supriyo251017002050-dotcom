#!/usr/bin/env python3
"""
fetch_contributions.py - Fetch GitHub contribution calendar & streak statistics
Outputs: contributions.json
"""

import json
import re
import sys
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# ===== CONFIGURATION =====
GH_USERNAME = "supriyo251017002050-dotcom"
OUTPUT_FILE = "contributions.json"
# =========================


def fetch_contributions(username):
    """Scrape GitHub contribution calendar from the public profile endpoint."""
    url = f"https://github.com/users/{username}/contributions"
    print(f"[*] Fetching contribution history for: @{username}")
    print(f"    Source URL: {url}")

    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
            timeout=15,
        )
        response.raise_for_status()
    except Exception as err:
        print(f"[!] Error fetching profile contributions: {err}")
        sys.exit(1)

    soup = BeautifulSoup(response.text, "html.parser")
    days = soup.find_all("td", class_="ContributionCalendar-day")

    contributions = []
    for day in days:
        date = day.get("data-date")
        count = 0

        tooltip = day.find_next_sibling("tool-tip")
        tooltip_text = tooltip.get_text(" ", strip=True) if tooltip else ""

        if tooltip_text:
            match = re.search(r"(\d+) contributions?", tooltip_text)
            if match:
                count = int(match.group(1))
            elif "No contributions" not in tooltip_text:
                count = int(day.get("data-level", 0))
        else:
            count = int(day.get("data-level", 0))

        if date:
            contributions.append({"date": date, "count": count})

    # Sort chronologically by date
    contributions.sort(key=lambda x: x["date"])

    total = sum(c["count"] for c in contributions)

    # Streak calculation
    longest_streak = 0
    temp_streak = 0
    for c in contributions:
        if c["count"] > 0:
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 0

    current_streak = 0
    for c in reversed(contributions):
        if c["count"] > 0:
            current_streak += 1
        else:
            break

    data = {
        "username": username,
        "fetched_at": datetime.now().isoformat(),
        "contributions": contributions,
        "total_contributions": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
    }

    print(f"[+] Total days tracked: {len(contributions)}")
    print(f"[+] Total contributions: {total}")
    print(f"[+] Current active streak: {current_streak} days")
    print(f"[+] Longest recorded streak: {longest_streak} days")

    return data


def save_json(data, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[+] Saved contributions to: {output_path}")


if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else GH_USERNAME
    data = fetch_contributions(user)
    save_json(data, OUTPUT_FILE)
