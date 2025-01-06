import os
import pandas as pd

# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define input files
dbr_input_file = os.path.join(script_dir, "danbooru_tags_2024-12-22_pt2-ia-dd-ed.csv")
e6_input_file = os.path.join(script_dir, "modified_e621_tags.csv")

# Read CSV files without headers
dbr_df = pd.read_csv(dbr_input_file, header=None)
e6_df = pd.read_csv(e6_input_file, header=None)

# Concatenate both DataFrames
merged_df = pd.concat([dbr_df, e6_df], ignore_index=True)

# Group by the first column (index 0) and aggregate
# Second and third columns (index 1 and 2) are taken from the first CSV (dbr_df)
# Fourth column (index 3) is a concatenation of unique values from both
result_df = (
    merged_df.groupby(0, as_index=False)
    .agg({
        1: 'first',  # Take the first value (from danbooru CSV)
        2: 'first',  # Take the first value (from danbooru CSV)
        3: lambda x: ','.join(sorted(set(
            [item.strip() for val in x.dropna() for item in val.split(',') if item.strip()]  # Flatten and deduplicate
        )))  # Merge unique, non-NaN strings and remove duplicates
    })
)


# Sort the result by the third column (index 2) in descending order
result_df = result_df.sort_values(by=2, ascending=False)

# Save the modified DataFrame as a CSV file
output_file = os.path.join(script_dir, "danbooru_e621_D.csv")
result_df.to_csv(output_file, index=False, header=False)

print(f"Modified CSV saved to: {output_file}")
