import json
import os

import pandas as pd

# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

fn_temp = "e621_tags_2024-12-22_pt2-ia-dd-ed.csv"
# danbooru_tags_2024-12-25_pt0-ia-dd-ed.csv
# e621_tags_2024-12-25_pt0-ia-dd-ed
# DBRE6_merged_tags_2024-12-25_pt0-ia-dd-ed

# File names
input_file = os.path.join(script_dir, fn_temp)  # Input CSV file in the same directory
output_file = os.path.join(script_dir, "A_" + fn_temp)  # Output CSV file in the same directory
blacklisted_tags_file = os.path.join(
    script_dir, "blacklisted_tags.json"
)  # Blacklisted tags JSON file in same directory

# Load the CSV file into a DataFrame
df = pd.read_csv(input_file)

def run():
    # Load the blacklisted tags from the JSON file
    with open(blacklisted_tags_file, "r") as f:
        blacklisted_tags_data = json.load(f)

    # Combine all blacklisted tags from both categories into a single list
    blacklisted_tags = blacklisted_tags_data.get("dbr", []) + blacklisted_tags_data.get("e621", [])

    # Filter out rows that contain blacklisted tags
    df = df[~df.iloc[:, 0].isin(blacklisted_tags)]
    return df

df = run()
# Save the updated DataFrame to the output file
df.to_csv(output_file, index=False)

print(f"Filtered data saved to {output_file}")
