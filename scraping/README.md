# SI568 Project 3

Scrapes the UMSI faculty directory at `https://www.si.umich.edu/people/directory/faculty`
and saves a CSV of faculty names with condensed role titles.

## Files

- `script.py`: fetches the faculty directory and extracts the data
- `requirements.txt`: Python dependencies
- `umsi_faculty.csv`: generated output file

## Output

Running the scraper creates or overwrites `umsi_faculty.csv` in this folder.

The CSV contains two columns:

- `name`
- `role`

Examples of condensed roles:

- `Lecturer I`
- `Associate Professor`
- `Adjunct Lecturer`
- `Professor Emeritus`

## Setup

```bash
cd scraping
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python script.py
```

## Notes

- The scraper makes a live request to the UMSI faculty directory.
- Roles are normalized from the full site text to shorter titles when possible.
- If the site markup changes, the scraper may need selector updates.
