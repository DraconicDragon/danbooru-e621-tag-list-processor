import os
import re

import pandas as pd

# experimental file to remove all but a certain category and then turn it into a txt/wildcard format
# based on X amount of entries
# this has nothing to do with the gender wildcard stuff
# can be used to make general artist/character/copyright wildcards tho

script_dir = os.path.dirname(os.path.abspath(__file__))

input_file = os.path.join(script_dir, "danbooru_tags_2024-11-15_pt50-ia-dd_cleaner.csv")
output_file = os.path.join(script_dir, "output.csv")

df = pd.read_csv(input_file)

# Filter rows where 'category' is "4" and 'count' is >= 100
# filtered_df = df[(df["category"] == 4) & (df["count"] >= 100)]

# category only then
filtered_df = df[df.iloc[:, 1] == 3]
# Keep only the top 100 entries
filtered_df = filtered_df.iloc[:100]


# remove the 'category', 'count', and 'aliases' columns
# filtered_df = filtered_df.drop(columns=["category", "count", "aliases"], errors="ignore") # named columns
filtered_df = filtered_df.drop(filtered_df.columns[[1, 2, 3]], axis=1, errors="ignore")  # unnamed

# string replacement and regex on remaining columns
for col in filtered_df.columns:
    filtered_df[col] = filtered_df[col].astype(str)  # make sure data is treated as strings
    filtered_df[col] = filtered_df[col].str.replace(
        "_", " ", regex=False
    )  # NOTE: comment this and bottom line to get tag lists instead of wildcard format
    filtered_df[col] = filtered_df[col].apply(lambda x: re.sub(r"([\(\)])", r"\\\1", x))

filtered_df.to_csv(output_file, index=False)

print(f"Filtered data saved to {output_file}")
