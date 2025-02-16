import os
import re

import pandas as pd

# removes rows from a CSV file where third column/post count is below a certain threshold

script_dir = os.path.dirname(os.path.abspath(__file__))

fn_temp = "danbooru_e621_merged_tags_2024-12-22_pt25-ia-dd-ed_refined-aliases.csv"
# danbooru_tags_2024-12-25_pt0-ia-dd-ed.csv
# e621_tags_2024-12-25_pt0-ia-dd-ed.csv
# DBRE6_merged_tags_2024-12-25_pt0-ia-dd-ed.csv

input_file = os.path.join(script_dir, fn_temp)

# Extract the current threshold from filename
match = re.search(r"pt(\d+)", fn_temp)
if match:
    current_threshold = int(match.group(1))
else:
    raise ValueError("Filename does not contain a valid threshold (e.g., 'pt25').")

# user input for desired post count threshold
# hardcoded because lazy, comment out with other stuff to make work otherwise, cryptic comment right here
desired_threshold = 25000
while not True:
    try:
        desired_threshold = int(
            input(f"Enter the desired post count threshold (must be greater than {current_threshold}): ")
        )
        if desired_threshold > current_threshold:
            break
        else:
            print(f"Threshold must be greater than {current_threshold}. Please try again.")
    except ValueError:
        print("Invalid input. Please enter a valid integer.")

# make new filename
new_fn_temp = fn_temp.replace(f"pt{current_threshold}", f"pt{desired_threshold}")
# new_fn_temp = "danbooru_e621_A.csv"
output_file = os.path.join(script_dir, new_fn_temp)

df = pd.read_csv(input_file)

# Filter DataFrame based on threshold
df = df[df.iloc[:, 2] >= desired_threshold]

df.to_csv(output_file, index=False)

print(f"Filtered data saved to {output_file}")
