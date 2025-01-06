import os

import pandas as pd

# changes the tag csvs to have a header and filters out categories 6 7 8 in e621 to create krita ai diffusion compatibility
# merged is not needed because krita lets you select multiple csvs at once

script_dir = os.path.dirname(os.path.abspath(__file__))

input_file = os.path.join(script_dir, "danbooru_tags_2024-12-25_pt25-ia-dd-ed.csv")
output_file = os.path.join(script_dir, "Danbooru NSFW.csv")  # Required name for krita ai

# Read CSV file ***without headers***
df = pd.read_csv(input_file, header=None)

# add headers required by krita ai
df.columns = ["tag", "type", "count", "aliases"]

if "type" in df.columns:
    # filter out rows where "type" column equals 6, 7, or 8
    df = df[(df["type"] != 6) & (df["type"] != 7) & (df["type"] != 8)]
else:
    print("Error: The 'type' column is not present in the dataset.")

df.to_csv(output_file, index=False)

print(f"Filtered data saved to {output_file}")
