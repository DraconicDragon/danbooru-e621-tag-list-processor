import os

import pandas as pd

# turn the gendered wildcard txt files into a csv file sorted by post count per gender

script_dir = os.path.dirname(os.path.abspath(__file__))

female_file = os.path.join(script_dir, "female_tags_sorted_post_count_full.txt")
male_file = os.path.join(script_dir, "male_tags_sorted_post_count_full.txt")
indeterminate_file = os.path.join(script_dir, "indeterminate_tags_sorted_post_count_full.txt")

csv_file = os.path.join(script_dir, "danbooru_tags_2024-12-22_pt2-ia-dd-ed.csv")
output_file = os.path.join(script_dir, "danbooru_characters_by_gender.csv")


# process txt tags
def process_text_file(file_path, gender):
    with open(file_path, "r", encoding="utf-8") as f:
        tags = [line.strip().replace(" ", "_").replace("\\", "") for line in f.readlines() if line.strip()]
    return [(tag, gender) for tag in tags]


data = process_text_file(female_file, "female")
data += process_text_file(male_file, "male")
data += process_text_file(indeterminate_file, "indeterminate")


columns = ["name", "gender"]
tags_df = pd.DataFrame(data, columns=columns)


danbooru_df = pd.read_csv(
    csv_file, header=None, usecols=[0, 1, 2], names=["name", "type", "post_count"], encoding="utf-8"
)

# Filter rows where type column is 4
danbooru_df = danbooru_df[danbooru_df["type"] == 4]

# remove rows with no/empty data
tags_df.dropna(inplace=True)
danbooru_df.dropna(inplace=True)


df_merged = tags_df.merge(danbooru_df, on="name", how="inner")

df_merged.dropna(inplace=True)

# Keep only relevant columns
final_df = df_merged[["name", "gender", "post_count"]]

final_df.to_csv(output_file, index=False, encoding="utf-8")

# Make sure no extra blank lines are appended to avoid trailing newlines
with open(output_file, "r+", encoding="utf-8") as f:
    content = f.read().rstrip()  # Remove trailing newlines + whitespace
    f.seek(0)
    f.write(content)
    f.truncate()  # Ensure no leftover data
    print(f"Combined CSV created at: {output_file}")
