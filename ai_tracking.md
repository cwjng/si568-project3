User: how can i read in the new csv files from data into this file to put in a pnadas dataframe/

GitHub Copilot: I’ll check your current dataprocessing.py so I can give you the exact import/read code using your project paths.

Read [](file:///Users/rebeccafalash/Desktop/si_568/si568-project3-team6/dataprocessing.py)

I’m going to add ready-to-run pandas loading helpers in dataprocessing.py so you can read both CSVs with the correct relative paths from this repo.

Generating patch (32 lines) in [](file:///Users/rebeccafalash/Desktop/si_568/si568-project3-team6/dataprocessing.py)

Read [](file:///Users/rebeccafalash/Desktop/si_568/si568-project3-team6/dataprocessing.py)

Generating patch (33 lines) in [](file:///Users/rebeccafalash/Desktop/si_568/si568-project3-team6/dataprocessing.py)


```

```
I added the loader code; next I’ll quickly validate there are no editor errors in dataprocessing.py.

Checked [](file:///Users/rebeccafalash/Desktop/si_568/si568-project3-team6/dataprocessing.py), 1 problem found

Read [](file:///Users/rebeccafalash/Desktop/si_568/si568-project3-team6/dataprocessing.py)

You can now read both CSV files directly in dataprocessing.py.

I added:
- A reusable loader in dataprocessing.py
- A function that loads both files into DataFrames in dataprocessing.py
- A small main block to print previews in dataprocessing.py

Use it like this in the same file:
- faculty_df = load_csv("umsi-faculty-ratings.csv")
- posts_df = load_csv("umsi-rating-posts.csv")
- all_dfs = load_all_dataframes()

One thing to fix first: your editor reports pandas is not installed in the current environment. Install it with:
pip install pandas

If you want, I can also add a quick merge/join example between the two DataFrames based on common columns.

Made changes.