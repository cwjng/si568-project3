from pathlib import Path
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup


FACULTY_URL = "https://www.si.umich.edu/people/directory/faculty"
STAFF_URL = "https://www.si.umich.edu/people/directory/staff"
HEADERS = {"User-Agent": "Mozilla/5.0"}

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_PATH = DATA_DIR / "umsi-faculty-list.csv"

TITLE_PATTERNS = [
    "Adjunct Clinical Assistant Professor",
    "Clinical Assistant Professor",
    "Adjunct Clinical Associate Professor",
    "Clinical Associate Professor",
    "Clinical Professor",
    "Associate Professor Emerita",
    "Associate Professor Emeritus",
    "Professor Emerita",
    "Professor Emeritus",
    "Assistant Professor",
    "Associate Professor",
    "Teaching Professor",
    "Intermittent Lecturer",
    "Adjunct Lecturer",
    "Lecturer [IVX]+",
    "Lecturer",
    "Professor",
]


def condense_role(raw_role):
    if not raw_role:
        return None

    for pattern in TITLE_PATTERNS:
        match = re.search(rf"\b({pattern})\b(?=\s+(?:of|in)\s+Information\b)", raw_role)
        if match:
            return match.group(1)

    for pattern in TITLE_PATTERNS:
        match = re.search(rf"\b({pattern})\b", raw_role)
        if match:
            return match.group(1)

    return raw_role.split(",")[0].strip()


def is_lecturer_or_professor(role):
    return bool(role) and ("Lecturer" in role or "Professor" in role)


def scrape_directory(url, role_filter=None):
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    rows = []
    seen_names = set()

    for card in soup.select("div.research-person-profile"):
        name_tag = card.select_one("h2.research-person-profile__name a")
        role_tag = card.select_one("div.research-person-profile__job-title")

        name = name_tag.get_text(" ", strip=True) if name_tag else None
        raw_role = role_tag.get_text(" ", strip=True) if role_tag else None
        role = condense_role(raw_role)

        if not name or not role or name in seen_names:
            continue
        if role_filter and not role_filter(role):
            continue

        seen_names.add(name)
        rows.append({"name": name, "role": role})

    if not rows:
        raise ValueError(f"No matching entries were found at {url}")

    return pd.DataFrame(rows)


def build_dataset():
    faculty_df = scrape_directory(FACULTY_URL)
    staff_df = scrape_directory(STAFF_URL, role_filter=is_lecturer_or_professor)

    combined_df = pd.concat([faculty_df, staff_df], ignore_index=True)
    combined_df = combined_df.sort_values("name", kind="stable").reset_index(drop=True)
    combined_df.insert(0, "id", range(1, len(combined_df) + 1))

    return combined_df


def main():
    DATA_DIR.mkdir(exist_ok=True)
    df = build_dataset()
    df.to_csv(OUTPUT_PATH, index=False, na_rep="")
    print(f"Saved {len(df)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
