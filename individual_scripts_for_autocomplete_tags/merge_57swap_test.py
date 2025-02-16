import os

import pandas as pd

# this is for merging the two CSV files but with category 5 and 7 swapped

script_dir = os.path.dirname(os.path.abspath(__file__))

dbr_input_file = os.path.join(script_dir, "danbooru_tags_2024-12-22_pt2-ia-dd-ed.csv")
e6_input_file = os.path.join(script_dir, "modified_new_cat_e621_tags.csv")

# Read CSV files ***without headers***
dbr_df = pd.read_csv(dbr_input_file, header=None)
e6_df = pd.read_csv(e6_input_file, header=None)

# swap rows in e6_df where the 2nd column value is 5 with 7 and vice versa
e6_df.loc[e6_df[1] == 5, 1] = -999  # temporary value
e6_df.loc[e6_df[1] == 7, 1] = 5
e6_df.loc[e6_df[1] == -999, 1] = 7

merged_df = pd.concat([dbr_df, e6_df], ignore_index=True)

# group by first column (index 0) and aggregate
# values of second and third columns are taken from first danbooru CSV (see comment below )
# Fourth column is concatenation of unique values from both; aliases merged if main tag is aggregated
result_df = merged_df.groupby(0, as_index=False).agg(
    {
        1: "first",  # take first value from danbooru CSV
        2: "first",  # take first value from danbooru CSV
        3: lambda x: ",".join(
            sorted(
                set(
                    [
                        item.strip() for val in x.dropna() for item in val.split(",") if item.strip()
                    ]  # Flatten and deduplicate
                )
            )
        ),  # Merge unique, non-NaN strings and remove duplicates
    }
)

# sort by third column (index 2) value
result_df = result_df.sort_values(by=2, ascending=False)

output_file = os.path.join(script_dir, "danbooru_e621_aggregated.csv")
result_df.to_csv(output_file, index=False, header=False)

print(f"Modified CSV saved to: {output_file}")
