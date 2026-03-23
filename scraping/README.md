# SI568 Project 3

This project has five data-building scripts:

- `script.py` builds the base UMSI faculty dataset.
- `ratings.py` enriches that dataset with Rate My Professors links, summary metrics, and top-tag indicator columns.
- `fetch_all_ratings.py` fetches all rating posts for a single Rate My Professors professor URL.
- `export_ratings_json.py` exports one JSON file per faculty member with a `rating_url`.
- `build_rating_posts_csv.py` builds a row-level dataset with one row per unique rating post.

## Scrapers

### `script.py`

`script.py` does all of the following in one run:

- scrapes the UMSI faculty directory
- scrapes the UMSI staff directory
- keeps only rows whose condensed role includes `Lecturer` or `Professor`
- combines both sets of rows
- sorts the final dataset alphabetically by `name`
- adds a unique sequential `id` column

Input sites:

- `https://www.si.umich.edu/people/directory/faculty`
- `https://www.si.umich.edu/people/directory/staff`

Output:

- `data/umsi-faculty-list.csv`

Output columns:

- `id`
- `name`
- `role`

### `ratings.py`

`ratings.py` reads the ratings dataset when it already exists, or falls back to the faculty list as its source. It then:

- reads each `rating_url`
- fetches the professor's Rate My Professors profile page
- extracts `num_ratings`
- extracts `overall_rating`
- extracts `would_take_again`
- extracts `level_of_difficulty`
- extracts the profile's Top Tags
- writes each supported tag as a `1` or `0` indicator column

Output:

- `data/umsi-faculty-ratings.csv`

Required source column:

- `rating_url`

Ratings output columns added or refreshed by `ratings.py`:

- `num_ratings`
- `overall_rating`
- `would_take_again`
- `level_of_difficulty`
- `tough_grader`
- `get_ready_to_read`
- `participation_matters`
- `extra_credit`
- `group_projects`
- `amazing_lectures`
- `clear_grading_criteria`
- `gives_good_feedback`
- `inspirational`
- `lots_of_homework`
- `hilarious`
- `beware_of_pop_quizzes`
- `so_many_papers`
- `caring`
- `respected`
- `lecture_heavy`
- `test_heavy`
- `graded_by_few_things`
- `accessible_outside_class`
- `online_savvy`

Tag columns use `1` when the tag is present on the professor profile and `0` otherwise.

### `fetch_all_ratings.py`

`fetch_all_ratings.py` pages through the Rate My Professors GraphQL endpoint for one professor URL and returns every visible rating post for that professor.

Output fields include:

- teacher metadata
- `num_ratings`
- one `ratings` array entry per rating post
- per-rating `qualityRating`
- per-rating `ratingTags`

Usage:

```bash
cd scraping
python fetch_all_ratings.py https://www.ratemyprofessors.com/professor/2100355
python fetch_all_ratings.py https://www.ratemyprofessors.com/professor/2100355 --output hess.json
```

### `export_ratings_json.py`

`export_ratings_json.py` reads `data/umsi-faculty-ratings.csv`, fetches all ratings for every row with a `rating_url`, and writes one JSON file per faculty member.

Output:

- `data/json/*.json`

Each file includes:

- `faculty_id`
- `name`
- `role`
- Rate My Professors teacher metadata
- a `ratings` array with every fetched rating post

Usage:

```bash
cd scraping
python export_ratings_json.py
```

### `build_rating_posts_csv.py`

`build_rating_posts_csv.py` reads the files in `data/json/` and builds a normalized post-level CSV where each row is one unique rating post.

Output:

- `data/umsi-rating-posts.csv`

Output columns:

- `id`
- `faculty_id`
- `text`
- `score`
- `date`
- `course`
- `tough_grader`
- `get_ready_to_read`
- `participation_matters`
- `extra_credit`
- `group_projects`
- `amazing_lectures`
- `clear_grading_criteria`
- `gives_good_feedback`
- `inspirational`
- `lots_of_homework`
- `hilarious`
- `beware_of_pop_quizzes`
- `so_many_papers`
- `caring`
- `respected`
- `lecture_heavy`
- `test_heavy`
- `graded_by_few_things`
- `accessible_outside_class`
- `online_savvy`

Notes for this dataset:

- `faculty_id` is a foreign key to `data/umsi-faculty-ratings.csv:id`
- `score` comes from the post-level Rate My Professors rating score
- `date` is stored as `YYYY-MM-DD`
- `text` is whitespace-normalized before writing the CSV
- tag columns are expanded from each post's `ratingTags` field and stored as `1` or `0`

Usage:

```bash
cd scraping
python build_rating_posts_csv.py
```

## Setup

```bash
cd scraping
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

Build the base faculty list:

```bash
cd scraping
python script.py
```

Refresh ratings and top-tag indicators:

```bash
cd scraping
python ratings.py
```

Export all per-faculty rating JSON files:

```bash
cd scraping
python export_ratings_json.py
```

Build the row-level rating-post CSV:

```bash
cd scraping
python build_rating_posts_csv.py
```

## Notes

- Roles are condensed from the full site text to shorter titles such as `Lecturer I` or `Associate Professor`.
- Faculty and staff rows that do not condense to a lecturer/professor title are excluded.
- `ratings.py` uses the existing ratings CSV as its source when available so it can preserve and refresh rows that already include `rating_url`.
- `export_ratings_json.py` writes generated files under `data/json/`.
- `build_rating_posts_csv.py` depends on the JSON files generated by `export_ratings_json.py`.
- If either site's markup changes, the scraper selectors or regex extraction may need to be updated.
