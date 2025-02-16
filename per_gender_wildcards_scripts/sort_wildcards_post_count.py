import os

import pandas as pd

# sorts the wildcard txt files by post count using the CSV data
# todo: the wildcard should really be in a csv format to begin with before becoming txt

script_dir = os.path.dirname(os.path.abspath(__file__))

female_file = os.path.join(script_dir, "new_female_tags.txt")
male_file = os.path.join(script_dir, "new_male_tags.txt")
indeterminate_file = os.path.join(script_dir, "new_indeterminate_tags.txt")

csv_file = os.path.join(script_dir, "danbooru_tags_2024-12-22_pt2-ia-dd-ed.csv")

print("Loading CSV data...")
try:
    df = pd.read_csv(csv_file, header=None, usecols=[0, 2], names=["tag", "post_count"])
    print("CSV loaded successfully.")
except Exception as e:
    print(f"Error loading CSV: {e}")
    exit(1)


def preprocess_tag(tag):
    return tag.replace(" ", "_").replace("\\", "")


def sort_tags(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as file:
        tags = file.read().splitlines()

    # Preprocess tags to match CSV format
    # processed_tags = [preprocess_tag(tag) for tag in tags]

    # Create a mapping of tags to post_count using the CSV data
    tag_to_count = df.set_index("tag")["post_count"].to_dict()

    # sort tags based on post_count, defaulting to 0 if not found in CSV
    # todo: print if not found in CSV
    sorted_tags = sorted(tags, key=lambda tag: tag_to_count.get(preprocess_tag(tag), 0), reverse=True)

    # Save sorted files
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("\n".join(sorted_tags))
    print(f"Sorted tags saved to: {file_path}")


sort_tags(female_file)
sort_tags(male_file)
sort_tags(indeterminate_file)
