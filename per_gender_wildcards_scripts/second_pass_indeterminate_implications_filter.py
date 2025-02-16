import os

import pandas as pd

# second pass indeterminate tags filter by using implications csv and filtering out related implications
# todo: does not respect tag_(female) naming etc, needs to be done separately
# NOTE: this operation takes surprisingly long, not as long as scraping each character tag however lol


script_dir = os.path.dirname(os.path.abspath(__file__))

input_file = os.path.join(script_dir, "sorted_tag_implications.csv")

female_file = os.path.join(script_dir, "female_sorted_top_full.txt")
male_file = os.path.join(script_dir, "male_sorted_top_full.txt")
indeterminate_file = os.path.join(script_dir, "indeterminate_sorted_top_full.txt")

# new files to modify
new_female_file = os.path.join(script_dir, "new_female_tags.txt")
new_male_file = os.path.join(script_dir, "new_male_tags.txt")
new_indeterminate_file = os.path.join(script_dir, "new_indeterminate_tags.txt")

print(f"Loading CSV file: {input_file}")
df = pd.read_csv(input_file)
print(f"CSV loaded successfully with {len(df)} rows.")


# Load existing tags into sets for faster lookups
def load_tags(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return set(tag.strip() for tag in f.readlines())
    return set()


print(f"Loading existing tags...")
male_tags = load_tags(male_file)
female_tags = load_tags(female_file)
indeterminate_tags = load_tags(indeterminate_file)

print(f"Tags loaded:")
print(f"- Male: {len(male_tags)}")
print(f"- Female: {len(female_tags)}")
print(f"- Indeterminate: {len(indeterminate_tags)}")

# Initialize new tag sets
new_male_tags = male_tags.copy()
new_female_tags = female_tags.copy()
new_indeterminate_tags = indeterminate_tags.copy()


print(f"Processing indeterminate tags...")
for indeterminate_tag in indeterminate_tags:
    indeterminate_tag_processed = indeterminate_tag.replace(" ", "_").replace("\\", "")

    for _, row in df.iterrows():
        antecedent_names = row["antecedent_names"].split(",")

        # check all antecedent names
        if any(indeterminate_tag_processed == antecedent.strip() for antecedent in antecedent_names):
            consequent_name = row["consequent_name"]
            consequent_name_processed = consequent_name.replace("_", " ").replace("(", r"\(").replace(")", r"\)")

            if consequent_name_processed in male_tags:
                if indeterminate_tag not in new_male_tags:
                    new_male_tags.add(indeterminate_tag)
                    print(f"Added '{indeterminate_tag}' to new male tags.")
                new_indeterminate_tags.discard(indeterminate_tag)

            elif consequent_name_processed in female_tags:
                if indeterminate_tag not in new_female_tags:
                    new_female_tags.add(indeterminate_tag)
                    print(f"Added '{indeterminate_tag}' to new female tags.")
                new_indeterminate_tags.discard(indeterminate_tag)

            # Stop processing once match is found
            break


def write_tags(file_path, tags):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(tags)) + "\n")


print(f"Writing updated tag files...")
write_tags(new_male_file, new_male_tags)
write_tags(new_female_file, new_female_tags)
write_tags(new_indeterminate_file, new_indeterminate_tags)

print(f"Finished processing all indeterminate tags.")
print(
    f"New files updated:\n"
    f"- Female: {new_female_file}\n"
    f"- Male: {new_male_file}\n"
    f"- Indeterminate: {new_indeterminate_file}"
)
