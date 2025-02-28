import os
import sys

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from tag_lists.merge_utils import merge_dbr_e6_tags, sanitize_aliases_merged

# script for merging individual tag lists from danbooru and e621 after they've been created already but not merged
# it uses the function from the main python files so it'll be aligned with the main tag merge methods if that changes

# this script's path
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define input files
dbr_input_file = os.path.join(script_dir, "danbooru_2025-02-16_pt25-ia-dd.csv")
e6_input_file = os.path.join(script_dir, "e621_2025-02-16_pt25-ia-ed.csv")
output_file = os.path.join(script_dir, "danbooru_e621_merged_2025-02-16_pt25-ia-dd-ed_sum.csv")

dbr_df = pd.read_csv(dbr_input_file, header=None)
e6_df = pd.read_csv(e6_input_file, header=None)

# add headers to the dfs
dbr_df.columns = ["name", "category", "post_count", "aliases"]
e6_df.columns = ["name", "category", "post_count", "aliases"]

merged_post_count_type = int(input("Enter merged_post_count_type (1: Danbooru, 2: e621, 3: Sum of Both): "))
# Determine the aggregation function for post_count based on merged_post_count_type
if merged_post_count_type == 1:
    post_count_agg = "first"  # Take the first value (from danbooru)
elif merged_post_count_type == 2:
    post_count_agg = lambda x: x.iloc[1] if len(x) > 1 else x.iloc[0]  # Take the second value (from e621)
elif merged_post_count_type == 3:
    post_count_agg = "sum"  # sum of both post counts (danbooru + e621)
else:
    raise ValueError(f"Invalid merged_post_count_type. merged_post_count_type: {merged_post_count_type}")


merged_df = merge_dbr_e6_tags(dbr_df, e6_df, merged_post_count_type)
result_df = sanitize_aliases_merged(merged_df)  # clean aliases so autocompletes dont reference wrong tags

# Save the modified DataFrame as a CSV file
result_df.to_csv(output_file, index=False, header=False)

print(f"Modified CSV saved to: {output_file}")
