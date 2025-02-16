import json
import os

# file to filter tags from indeterminate out/around based on json file with keys for each gender
# todo: needs to be able to do male/female too since those contain false positives, eg: kirby is in male but is androgynous

script_dir = os.path.dirname(os.path.abspath(__file__))

female_file = os.path.join(script_dir, "female_tags_sorted_post_count_full.txt")
male_file = os.path.join(script_dir, "male_tags_sorted_post_count_full.txt")
indeterminate_file = os.path.join(script_dir, "indeterminate_tags_sorted_post_count_full.txt")
filter_file = os.path.join(script_dir, "hardcoded_tags_to_filter.json")

with open(filter_file, "r") as f:
    filters = json.load(f)


# read file, return list of lines
def read_file(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return f.read().splitlines()
    return []


# wirte list of lines to file, joined by newline '\n'
def write_file(filepath, lines):
    with open(filepath, "w") as f:
        f.write("\n".join(lines))


# Load files into lists
indeterminate_tags = read_file(indeterminate_file)
female_tags = read_file(female_file)
male_tags = read_file(male_file)

# Process indeterminate tags
updated_indeterminate_tags = []
for tag in indeterminate_tags:
    if tag in filters.get("female", []):
        female_tags.append(tag)
    elif tag in filters.get("male", []):
        male_tags.append(tag)
    else:
        updated_indeterminate_tags.append(tag)

# Write updated lists back to files
write_file(indeterminate_file, updated_indeterminate_tags)
write_file(female_file, sorted(set(female_tags)))  # avoid duplicates i guess
write_file(male_file, sorted(set(male_tags)))
