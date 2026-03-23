import csv
import json
import re
import time
from pathlib import Path

from fetch_all_ratings import fetch_all_ratings


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "umsi-faculty-ratings.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "json"
REQUEST_DELAY_SECONDS = 0.25


def slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "unknown"


def main():
    with INPUT_PATH.open(newline="", encoding="utf-8") as input_file:
        rows = list(csv.DictReader(input_file))

    rated_rows = [row for row in rows if row.get("rating_url", "").strip()]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for index, row in enumerate(rated_rows, start=1):
        professor_url = row["rating_url"].strip()
        file_name = f"{row['id']}-{slugify(row['name'])}.json"
        output_path = OUTPUT_DIR / file_name

        print(f"Fetching {index}/{len(rated_rows)}: {professor_url}")
        result = fetch_all_ratings(professor_url)
        result["faculty_id"] = row["id"]
        result["name"] = row["name"]
        result["role"] = row["role"]

        output_path.write_text(
            json.dumps(result, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        time.sleep(REQUEST_DELAY_SECONDS)

    print(f"Saved {len(rated_rows)} files to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
