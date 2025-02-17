import os

# sorts the text files by newline by alphabet

script_dir = os.path.dirname(os.path.abspath(__file__))

female_file = os.path.join(script_dir, "new_female_tags.txt")
male_file = os.path.join(script_dir, "new_male_tags.txt")
indeterminate_file = os.path.join(script_dir, "new_indeterminate_tags.txt")


def sort_tags_alphabetically(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"Processing file: {file_path}")
    with open(file_path, "r") as f:
        tags = [line.strip() for line in f.readlines()]

    print(f"Original tags in {file_path}: {tags[:8]}")

    sorted_tags = sorted(tags)

    print(f"Sorted tags in {file_path}: {sorted_tags[:8]}")

    with open(file_path, "w") as f:
        f.write("\n".join(sorted_tags))

    print(f"File {file_path} sorted and saved.")


for txt_file in [female_file, male_file, indeterminate_file]:
    sort_tags_alphabetically(txt_file)

print("Finished.")
