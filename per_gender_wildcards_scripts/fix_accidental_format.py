import os

import pandas as pd

# fixes accidentally formatted txt file tags to have underscores and backslashes and removes them

script_dir = os.path.dirname(os.path.abspath(__file__))

female_file = os.path.join(script_dir, "female_sorted_top_full.txt")
male_file = os.path.join(script_dir, "male_sorted_top_full.txt")
indeterminate_file = os.path.join(script_dir, "indeterminate_sorted_top_full.txt")


def modify_tags_in_file(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"Processing file: {file_path}")
    with open(file_path, "r") as f:
        tags = [line.strip() for line in f.readlines()]

    modified_tags = []
    for tag in tags:
        tag = tag.replace("_", " ")
        tag = tag.replace("(", "\\(").replace(")", "\\)")
        modified_tags.append(tag)

    with open(file_path, "w") as f:
        f.write("\n".join(modified_tags))

    print(f"File {file_path} modified and saved")


# go through each file and modify the tags
for txt_file in [female_file, male_file, indeterminate_file]:
    modify_tags_in_file(txt_file)

print("Done")
