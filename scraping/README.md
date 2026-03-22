# SI568 Project 3

`script.py` is the single scraper entry point for this project.

It does all of the following in one run:

- scrapes the UMSI faculty directory
- scrapes the UMSI staff directory
- keeps only rows whose condensed role includes `Lecturer` or `Professor`
- combines both sets of rows
- sorts the final dataset alphabetically by `name`
- adds a unique sequential `id` column

## Input Sites

- `https://www.si.umich.edu/people/directory/faculty`
- `https://www.si.umich.edu/people/directory/staff`

## Output

Running the script creates or overwrites:

- `data/umsi-faculty-list.csv`

The output columns are:

- `id`
- `name`
- `role`

## Setup

```bash
cd scraping
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python script.py
```

## Notes

- Roles are condensed from the full site text to shorter titles such as `Lecturer I` or `Associate Professor`.
- Faculty and staff rows that do not condense to a lecturer/professor title are excluded.
- If the site markup changes, the scraper selectors may need to be updated.
