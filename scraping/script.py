from pathlib import Path
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd


BASE_URL = "https://www.si.umich.edu/people/directory/faculty"
HEADERS = {"User-Agent": "Mozilla/5.0"}
OUTPUT_PATH = Path(__file__).with_name("umsi_faculty.csv")

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


def scrape_faculty():
    response = requests.get(BASE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    data = []
    seen_names = set()

    for card in soup.select("div.research-person-profile"):
        name_tag = card.select_one("h2.research-person-profile__name a")
        role_tag = card.select_one("div.research-person-profile__job-title")

        name = name_tag.get_text(" ", strip=True) if name_tag else None
        raw_role = role_tag.get_text(" ", strip=True) if role_tag else None
        role = condense_role(raw_role)
        if not name or not role or name in seen_names:
            continue

        seen_names.add(name)
        data.append(
            {
                "name": name,
                "role": role,
            }
        )

    if not data:
        raise ValueError("No faculty entries were found on the page. The site markup may have changed.")

    return pd.DataFrame(data).sort_values("name").reset_index(drop=True)


def main():
    df = scrape_faculty()
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df)} faculty to {OUTPUT_PATH.name}")


if __name__ == "__main__":
    main()
