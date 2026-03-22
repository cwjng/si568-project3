from pathlib import Path
import re
import time

import pandas as pd
import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "umsi-faculty-list.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "umsi-faculty-ratings.csv"
HEADERS = {"User-Agent": "Mozilla/5.0"}
REQUEST_DELAY_SECONDS = 0.25


def extract_legacy_id(rating_url):
    match = re.search(r"/professor/(\d+)", str(rating_url))
    return match.group(1) if match else None


def fetch_rating_summary(session, rating_url):
    if not isinstance(rating_url, str) or not rating_url.strip():
        return {
            "overall_rating": pd.NA,
            "would_take_again": pd.NA,
            "level_of_difficulty": pd.NA,
        }

    legacy_id = extract_legacy_id(rating_url)
    if not legacy_id:
        return {
            "overall_rating": pd.NA,
            "would_take_again": pd.NA,
            "level_of_difficulty": pd.NA,
        }

    try:
        response = session.get(rating_url, timeout=30)
        response.raise_for_status()
    except requests.RequestException:
        return {
            "overall_rating": pd.NA,
            "would_take_again": pd.NA,
            "level_of_difficulty": pd.NA,
        }

    html = response.text
    pattern = (
        rf'legacyId":{legacy_id}.*?'
        rf'numRatings":(\d+).*?'
        rf'avgRating":([0-9.]+).*?'
        rf'avgDifficulty":([0-9.]+).*?'
        rf'wouldTakeAgainPercent":(-?[0-9.]+)'
    )
    match = re.search(pattern, html)
    if not match:
        return {
            "overall_rating": pd.NA,
            "would_take_again": pd.NA,
            "level_of_difficulty": pd.NA,
        }

    num_ratings = int(match.group(1))
    avg_rating = float(match.group(2))
    avg_difficulty = float(match.group(3))
    would_take_again = float(match.group(4))

    if num_ratings == 0:
        return {
            "overall_rating": pd.NA,
            "would_take_again": pd.NA,
            "level_of_difficulty": pd.NA,
        }

    return {
        "overall_rating": avg_rating if avg_rating > 0 else pd.NA,
        "would_take_again": would_take_again if would_take_again >= 0 else pd.NA,
        "level_of_difficulty": avg_difficulty if avg_difficulty > 0 else pd.NA,
    }


def main():
    df = pd.read_csv(INPUT_PATH)

    if "rating_url" not in df.columns:
        raise ValueError(f"{INPUT_PATH} must include a rating_url column")

    session = requests.Session()
    session.headers.update(HEADERS)

    ratings_cache = {}
    overall_ratings = []
    would_take_again_values = []
    difficulty_values = []

    unique_urls = [url for url in df["rating_url"].dropna().unique() if str(url).strip()]

    for index, rating_url in enumerate(unique_urls, start=1):
        print(f"Fetching {index}/{len(unique_urls)}: {rating_url}")
        ratings_cache[rating_url] = fetch_rating_summary(session, rating_url)
        time.sleep(REQUEST_DELAY_SECONDS)

    for rating_url in df["rating_url"]:
        summary = ratings_cache.get(
            rating_url,
            {
                "overall_rating": pd.NA,
                "would_take_again": pd.NA,
                "level_of_difficulty": pd.NA,
            },
        )
        overall_ratings.append(summary["overall_rating"])
        would_take_again_values.append(summary["would_take_again"])
        difficulty_values.append(summary["level_of_difficulty"])

    df["overall_rating"] = overall_ratings
    df["would_take_again"] = would_take_again_values
    df["level_of_difficulty"] = difficulty_values
    df.to_csv(OUTPUT_PATH, index=False, na_rep="")

    print(f"Saved {len(df)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
