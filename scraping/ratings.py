from pathlib import Path
import json
import re
import time

import pandas as pd
import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "umsi-faculty-list.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "umsi-faculty-ratings.csv"
HEADERS = {"User-Agent": "Mozilla/5.0"}
REQUEST_DELAY_SECONDS = 0.25
TAG_COLUMNS = [
    "tough_grader",
    "get_ready_to_read",
    "participation_matters",
    "extra_credit",
    "group_projects",
    "amazing_lectures",
    "clear_grading_criteria",
    "gives_good_feedback",
    "inspirational",
    "lots_of_homework",
    "hilarious",
    "beware_of_pop_quizzes",
    "so_many_papers",
    "caring",
    "respected",
    "lecture_heavy",
    "test_heavy",
    "graded_by_few_things",
    "accessible_outside_class",
    "online_savvy",
]
TAG_LABEL_TO_COLUMN = {
    "Tough Grader": "tough_grader",
    "Get Ready To Read": "get_ready_to_read",
    "Participation Matters": "participation_matters",
    "Extra Credit": "extra_credit",
    "Group Projects": "group_projects",
    "Amazing Lectures": "amazing_lectures",
    "Clear Grading Criteria": "clear_grading_criteria",
    "Gives Good Feedback": "gives_good_feedback",
    "Inspirational": "inspirational",
    "Lots Of Homework": "lots_of_homework",
    "Hilarious": "hilarious",
    "Beware Of Pop Quizzes": "beware_of_pop_quizzes",
    "So Many Papers": "so_many_papers",
    "Caring": "caring",
    "Respected": "respected",
    "Lecture Heavy": "lecture_heavy",
    "Test Heavy": "test_heavy",
    "Graded By Few Things": "graded_by_few_things",
    "Accessible Outside Class": "accessible_outside_class",
    "Online Savvy": "online_savvy",
}
TAG_NAME_TO_COLUMN = {
    " ".join(tag.lower().split()): column for tag, column in TAG_LABEL_TO_COLUMN.items()
}


def extract_legacy_id(rating_url):
    match = re.search(r"/professor/(\d+)", str(rating_url))
    return match.group(1) if match else None


def build_empty_profile():
    profile = {
        "overall_rating": pd.NA,
        "would_take_again": pd.NA,
        "level_of_difficulty": pd.NA,
    }
    profile.update({column: 0 for column in TAG_COLUMNS})
    return profile


def normalize_tag_name(tag_name):
    return " ".join(str(tag_name).split()).lower()


def extract_teacher_tags(html, legacy_id):
    match = re.search(
        rf'"legacyId":{legacy_id}.*?"teacherRatingTags":{{"__refs":\[(.*?)\]}}',
        html,
        re.S,
    )
    if not match:
        return set()

    refs = re.findall(r'"([^"]+)"', match.group(1))
    tags = set()

    for ref in refs:
        ref_match = re.search(
            rf'"{re.escape(ref)}":{{.*?"tagName":"((?:\\.|[^"\\])*)"',
            html,
            re.S,
        )
        if not ref_match:
            continue
        decoded_tag = json.loads(f'"{ref_match.group(1)}"')
        tags.add(normalize_tag_name(decoded_tag))

    return tags


def fetch_rating_summary(session, rating_url):
    if not isinstance(rating_url, str) or not rating_url.strip():
        return build_empty_profile()

    legacy_id = extract_legacy_id(rating_url)
    if not legacy_id:
        return build_empty_profile()

    try:
        response = session.get(rating_url, timeout=30)
        response.raise_for_status()
    except requests.RequestException:
        return build_empty_profile()

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
        return build_empty_profile()

    num_ratings = int(match.group(1))
    avg_rating = float(match.group(2))
    avg_difficulty = float(match.group(3))
    would_take_again = float(match.group(4))

    tag_values = {column: 0 for column in TAG_COLUMNS}
    for tag_name in extract_teacher_tags(html, legacy_id):
        column = TAG_NAME_TO_COLUMN.get(tag_name)
        if column:
            tag_values[column] = 1

    if num_ratings == 0:
        profile = build_empty_profile()
        profile.update(tag_values)
        return profile

    profile = {
        "overall_rating": avg_rating if avg_rating > 0 else pd.NA,
        "would_take_again": would_take_again if would_take_again >= 0 else pd.NA,
        "level_of_difficulty": avg_difficulty if avg_difficulty > 0 else pd.NA,
    }
    profile.update(tag_values)
    return profile


def main():
    source_path = OUTPUT_PATH if OUTPUT_PATH.exists() else INPUT_PATH
    df = pd.read_csv(source_path)

    if "rating_url" not in df.columns:
        raise ValueError(f"{source_path} must include a rating_url column")

    session = requests.Session()
    session.headers.update(HEADERS)

    ratings_cache = {}
    overall_ratings = []
    would_take_again_values = []
    difficulty_values = []
    tag_values = {column: [] for column in TAG_COLUMNS}

    unique_urls = [url for url in df["rating_url"].dropna().unique() if str(url).strip()]

    for index, rating_url in enumerate(unique_urls, start=1):
        print(f"Fetching {index}/{len(unique_urls)}: {rating_url}")
        ratings_cache[rating_url] = fetch_rating_summary(session, rating_url)
        time.sleep(REQUEST_DELAY_SECONDS)

    for rating_url in df["rating_url"]:
        summary = ratings_cache.get(
            rating_url,
            build_empty_profile(),
        )
        overall_ratings.append(summary["overall_rating"])
        would_take_again_values.append(summary["would_take_again"])
        difficulty_values.append(summary["level_of_difficulty"])
        for column in TAG_COLUMNS:
            tag_values[column].append(summary[column])

    df["overall_rating"] = overall_ratings
    df["would_take_again"] = would_take_again_values
    df["level_of_difficulty"] = difficulty_values

    for column in TAG_COLUMNS:
        df[column] = tag_values[column]

    df.to_csv(OUTPUT_PATH, index=False, na_rep="")

    print(f"Saved {len(df)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
