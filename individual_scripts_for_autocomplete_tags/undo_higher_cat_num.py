import os

import pandas as pd

# script for when e621 csv with higher category for new merge exists but want to revert the higher category to normal

script_dir = os.path.dirname(os.path.abspath(__file__))

e6_input_file = os.path.join(script_dir, "new_cat_e621_tags.csv")

# Read csv file ***without headers***
e6_df = pd.read_csv(e6_input_file, header=None)

e6_df[1] = e6_df[1] - 7  # subtract 7 from all rows in second column/category value

output_file = os.path.join(script_dir, "modified_new_cat_e621_tags.csv")
e6_df.to_csv(output_file, index=False, header=False)

print(f"Modified CSV saved to: {output_file}")
