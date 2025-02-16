import os

# removes lines below a certain threshold (found in line_limits) from text files

script_dir = os.path.dirname(os.path.abspath(__file__))

female_file = os.path.join(script_dir, "female_sorted_top_full.txt")
male_file = os.path.join(script_dir, "male_sorted_top_full.txt")
indeterminate_file = os.path.join(script_dir, "indeterminate_sorted_top_full.txt")

# female_file = os.path.join(script_dir, "new_female_tags.txt")
# male_file = os.path.join(script_dir, "new_male_tags.txt")
# indeterminate_file = os.path.join(script_dir, "new_indeterminate_tags.txt")

files = [female_file, male_file, indeterminate_file]

# was getting too messy filling up main directory with all this
output_folder = os.path.join(script_dir, "lists/filtered_files")
os.makedirs(output_folder, exist_ok=True)

# hardcoded list of line limits
line_limits_female = [
    10,
    25,
    50,
    75,
    100,
    200,
    350,
    500,
    750,
    1000,
    1500,
    3555,
    5000,
    7500,
    10000,
    13333,
    16666,
    20000,
    25000,
    30000,
]
line_limits = [10, 25, 50, 75, 100, 200, 350, 500, 750, 1000, 1500, 2000, 3555, 5000, 8000]


def process_and_filter_text_file(file_path, line_limits_to_use):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.rstrip() for line in f if line.strip()]  # remove empty lines + strip trailing whitespace

        # make a file for every limt_limit value
        for limit in line_limits_to_use:
            # Keep only the top 'limit' lines
            lines_to_keep = lines[:limit]

            base_name = os.path.basename(file_path)  # add limit to filename by replacing "full"
            new_file_name = base_name.replace("full", str(limit))

            new_file_path = os.path.join(output_folder, new_file_name)

            with open(new_file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines_to_keep))  # write lines joined by '\n'

            print(f"Top {limit} lines saved to {new_file_path}")
    else:
        print(f"File {file_path} not found")


process_and_filter_text_file(female_file, line_limits_female)
process_and_filter_text_file(male_file, line_limits)
process_and_filter_text_file(indeterminate_file, line_limits)
