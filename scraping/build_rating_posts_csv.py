import csv
import html
import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = PROJECT_ROOT / "data" / "json"
OUTPUT_PATH = PROJECT_ROOT / "data" / "umsi-rating-posts.csv"
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
    " ".join(label.lower().split()): column
    for label, column in TAG_LABEL_TO_COLUMN.items()
}


def normalize_tag_name(tag_name):
    return " ".join(tag_name.split()).lower()


def parse_rating_tags(raw_tags):
    values = {column: 0 for column in TAG_LABEL_TO_COLUMN.values()}
    if not raw_tags:
        return values

    for tag in raw_tags.split("--"):
        column = TAG_NAME_TO_COLUMN.get(normalize_tag_name(tag))
        if column:
            values[column] = 1

    return values


def extract_date(raw_date):
    if not raw_date:
        return ""
    return raw_date.split(" ", 1)[0]


def clean_text(raw_text):
    return re.sub(r"\s+", " ", html.unescape(raw_text or "")).strip()


def build_rows():
    rows = []

    for path in sorted(INPUT_DIR.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        faculty_id = payload.get("faculty_id")

        for rating in payload.get("ratings", []):
            row = {
                "id": rating["legacyId"],
                "faculty_id": faculty_id,
                "text": clean_text(rating.get("comment") or ""),
                "score": rating.get("qualityRating", ""),
                "date": extract_date(rating.get("date") or ""),
                "course": rating.get("class") or "",
            }
            row.update(parse_rating_tags(rating.get("ratingTags") or ""))
            rows.append(row)

    return rows


def main():
    rows = build_rows()
    fieldnames = [
        "id",
        "faculty_id",
        "text",
        "score",
        "date",
        "course",
        *TAG_LABEL_TO_COLUMN.values(),
    ]

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
