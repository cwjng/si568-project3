import argparse
import base64
import json
import re

import requests


GRAPHQL_URL = "https://www.ratemyprofessors.com/graphql"
HEADERS = {"User-Agent": "Mozilla/5.0"}
PAGE_SIZE = 5
RATING_FIELDS = """
  legacyId
  class
  date
  comment
  helpfulRatingRounded
  difficultyRatingRounded
  clarityRatingRounded
  iWouldTakeAgain
"""
QUERY = f"""
query($id: ID!, $first: Int!, $after: String) {{
  node(id: $id) {{
    ... on Teacher {{
      id
      legacyId
      firstName
      lastName
      numRatings
      ratings(first: $first, after: $after) {{
        edges {{
          cursor
          node {{
{RATING_FIELDS}
          }}
        }}
        pageInfo {{
          hasNextPage
          endCursor
        }}
      }}
    }}
  }}
}}
"""


def extract_legacy_id(professor_url):
    match = re.search(r"/professor/(\d+)", professor_url)
    if not match:
        raise ValueError(f"Could not extract a professor id from {professor_url}")
    return match.group(1)


def encode_teacher_id(legacy_id):
    return base64.b64encode(f"Teacher-{legacy_id}".encode()).decode()


def fetch_all_ratings(professor_url):
    legacy_id = extract_legacy_id(professor_url)
    teacher_id = encode_teacher_id(legacy_id)

    session = requests.Session()
    session.headers.update(HEADERS)

    ratings = []
    after = None
    teacher = None

    while True:
        response = session.post(
            GRAPHQL_URL,
            json={
                "query": QUERY,
                "variables": {
                    "id": teacher_id,
                    "first": PAGE_SIZE,
                    "after": after,
                },
            },
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()

        if payload.get("errors"):
            raise RuntimeError(payload["errors"])

        teacher = payload["data"]["node"]
        if not teacher:
            raise ValueError(f"No teacher found for {professor_url}")

        connection = teacher["ratings"]
        ratings.extend(edge["node"] for edge in connection["edges"])

        page_info = connection["pageInfo"]
        if not page_info["hasNextPage"]:
            break
        after = page_info["endCursor"]

    return {
        "professor_url": professor_url,
        "teacher_id": teacher["id"],
        "legacy_id": teacher["legacyId"],
        "first_name": teacher["firstName"],
        "last_name": teacher["lastName"],
        "num_ratings": teacher["numRatings"],
        "ratings": ratings,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Fetch all Rate My Professors ratings for a professor URL."
    )
    parser.add_argument("professor_url", help="Rate My Professors professor URL")
    parser.add_argument(
        "-o",
        "--output",
        help="Optional path to write the JSON output",
    )
    args = parser.parse_args()

    result = fetch_all_ratings(args.professor_url)
    rendered = json.dumps(result, indent=2, ensure_ascii=True)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as output_file:
            output_file.write(rendered)
            output_file.write("\n")
        print(f"Saved {len(result['ratings'])} ratings to {args.output}")
        return

    print(rendered)


if __name__ == "__main__":
    main()
