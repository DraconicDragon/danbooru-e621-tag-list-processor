import os

import pandas as pd

# NOTE: not needed file, had brainfart, but dont want to delete it

script_dir = os.path.dirname(os.path.abspath(__file__))

female_file = os.path.join(script_dir, "female_tags_sorted_post_count_full.txt")
male_file = os.path.join(script_dir, "male_tags_sorted_post_count_full.txt")
indeterminate_file = os.path.join(script_dir, "indeterminate_tags_sorted_post_count_full.txt")

sort_file = os.path.join(script_dir, "sorted_tag_implications.csv")

print("Loading CSV data...")
try:
    df = pd.read_csv(sort_file)
    print("CSV loaded successfully.")
except Exception as e:
    print(f"Error loading CSV: {e}")
    exit(1)


# Preprocess CSV data
def preprocess_tag(tag):
    return tag.replace(" ", "_").replace("\\", "")


df["consequent_name"] = df["consequent_name"].apply(preprocess_tag)
df["antecedent_names"] = df["antecedent_names"].apply(
    lambda x: [preprocess_tag(tag) for tag in x.strip('"').split(",")]
)


# sort a file by post count of implications.csv, again NOTE: this is stupid lmao there arent even the same amount of tags
def sort_tags_in_file(file_path, df):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"Processing file: {file_path}")
    with open(file_path, "r") as f:
        tags = [preprocess_tag(line.strip()) for line in f.readlines()]  # preprocess txt file tags

    print(f"Original tags in {file_path}: {tags[:5]} (showing up to 5)")

    tag_priority = {}

    for tag in tags:
        matches = df[(df["consequent_name"] == tag) | (df["antecedent_names"].apply(lambda x: tag in x))]

        if not matches.empty:
            is_consequent = matches["consequent_name"].eq(tag).any()
            post_count = matches["post_count"].max()  # Use max post_count if multiple matches
            tag_priority[tag] = (is_consequent, post_count)
        else:
            tag_priority[tag] = (False, 0)  # default priority for no match

    # Sort tags: first by whether it's a consequent name, then by post count
    # NOTE: reuse this if other scripts cant put implications close to main tag but probably not needed
    sorted_tags = sorted(tags, key=lambda t: (-(1 if tag_priority[t][0] else 0), -tag_priority[t][1]))

    print(f"Sorted tags in {file_path}: {sorted_tags[:5]} (showing up to 5)")

    with open(file_path, "w") as f:
        f.write("\n".join(sorted_tags))

    print(f"File {file_path} sorted and saved.")


for txt_file in [female_file, male_file, indeterminate_file]:
    sort_tags_in_file(txt_file, df)

print("All files processed.")
