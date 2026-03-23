# SI568 Project 3

This project has two scraper entry points:

- `script.py` builds the base UMSI faculty dataset.
- `ratings.py` enriches that dataset with Rate My Professors links, summary metrics, and top-tag indicator columns.

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

## Notes

- Roles are condensed from the full site text to shorter titles such as `Lecturer I` or `Associate Professor`.
- Faculty and staff rows that do not condense to a lecturer/professor title are excluded.
- `ratings.py` uses the existing ratings CSV as its source when available so it can preserve and refresh rows that already include `rating_url`.
- If either site's markup changes, the scraper selectors or regex extraction may need to be updated.
