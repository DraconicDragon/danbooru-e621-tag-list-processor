import os

import pandas as pd

# script to remove tags that are already in column 1 from column 4
# (removing alias tags that already exist as normal tags removing false alias redirects like 1girl > female)


script_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(script_dir, "danbooru_e621_merged_tags_2024-12-22_pt2-ia-dd-ed.csv")
output_file = os.path.join(script_dir, "danbooru_e621_merged_tags_2024-12-22_pt2-ia-dd-ed_refined-aliases.csv")


def process_csv(input_file):
    df = pd.read_csv(input_file, header=None, dtype=str)

    # this so column 4 cant be NaN if no aliases
    df[3] = df[3].fillna("")

    # get all tags from column 1 into a set
    all_tags = set(df[0].str.strip())

    def remove_duplicate_tags(row):
        tags = row[3].strip()

        if not tags:  # skip empty tags
            return tags

        # split the aliases into list, strip spaces, remove any alias tag that already appears in column 1
        tag_list = [tag.strip() for tag in tags.split(",")]
        filtered_tags = [tag for tag in tag_list if tag not in all_tags]

        return ",".join(filtered_tags)

    # start filter column 4
    df[3] = df.apply(remove_duplicate_tags, axis=1)

    return df


result_df = process_csv(input_file)


result_df.to_csv(output_file, index=False, header=False)

print(f"Modified CSV saved to: {output_file}")
