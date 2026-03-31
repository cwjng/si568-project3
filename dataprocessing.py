from pathlib import Path
from typing import Dict

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def load_csv(filename: str) -> pd.DataFrame:
	file_path = DATA_DIR / filename
	return pd.read_csv(file_path)


def load_all_dataframes() -> Dict[str, pd.DataFrame]:
	return {
		"faculty_ratings": load_csv("umsi-faculty-ratings.csv"),
		"rating_posts": load_csv("umsi-rating-posts.csv"),
	}


dataframes = load_all_dataframes()
print(dataframes["faculty_ratings"].head())
print(dataframes["rating_posts"].head())




