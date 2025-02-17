import os

import pandas as pd

# This script increases the second column's value by 7 (0->7) from the given csv

# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define input files
e6_input_file = os.path.join(script_dir, "e621_tags_2024-12-22_pt25-ia-ed.csv")

# Read CSV files without headers
e6_df = pd.read_csv(e6_input_file, header=None)

e6_df[1] += 7

# Save the modified DataFrame as a CSV file
output_file = os.path.join(script_dir, "higher_e621_cat.csv")
e6_df.to_csv(output_file, index=False, header=False)  # Ensure the file is saved

print(f"Modified CSV saved to: {output_file}")
