import json
import os
import time

import pandas as pd
import requests

# Sort the DataFrame using the external CSV file
script_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(script_dir, "danbooru_tags_2024-12-22_pt2-ia-dd-ed.csv")


def get_dbr_jsons(dbr_url: str):
    """Scrape tag implications from Danbooru JSONs and process the data."""
    tag_data = []

    for page in range(1, 1001):
        url = f"{dbr_url}&page={page}"  # Update URL with current page

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            if not data:  # Break the loop if the data is empty (no more tags to fetch)
                print(f"(DBR) No more data found at page {page}. Stopping...", flush=True)
                break

            # Remove the 'reason' key from each dictionary
            for item in data:
                item.pop("reason", None)

            tag_data.extend(data)  # Append current page data to the list
            print(f"(DBR) Page {page} implications processed...", flush=True)
        else:
            print(f"(DBR) Failed to fetch page {page}. HTTP Status Code: {response.status_code}", flush=True)
            break

        time.sleep(0.3)  # Sleep for 0.3 second to help with rate limits

    # Save the data to a JSON file
    with open("tag_implications.json", "w") as f:
        json.dump(tag_data, f, indent=4)

    # Process the data for the DataFrame
    processed_data = {}
    for item in tag_data:
        consequent_name = item["consequent_name"]
        antecedent_name = item["antecedent_name"]
        status = item["status"]

        if consequent_name not in processed_data:
            processed_data[consequent_name] = {"antecedents": set(), "status": status}

        processed_data[consequent_name]["antecedents"].add(antecedent_name)

    # Create a DataFrame
    rows = [
        {
            "consequent_name": key,
            "antecedent_names": ",".join(sorted(value["antecedents"])),
            "status": value["status"],
        }
        for key, value in processed_data.items()
    ]

    tag_df = pd.DataFrame(rows, columns=["consequent_name", "antecedent_names", "status"])

    if os.path.exists(input_file):
        danbooru_csv = pd.read_csv(input_file, header=None, names=["name", "category", "post_count", "aliases"])

        # Filter the CSV for rows where the second column is 4
        filtered_csv = danbooru_csv[danbooru_csv["category"] == 4]

        # Create a mapping of consequent_name to post_count
        post_count_map = dict(zip(filtered_csv["name"], filtered_csv["post_count"]))

        # Add post_count to the DataFrame
        tag_df["post_count"] = tag_df["consequent_name"].map(post_count_map)

        # Sort the DataFrame by post_count (descending) and drop rows with NaN post_count
        tag_df = tag_df.dropna(subset=["post_count"]).sort_values(by="post_count", ascending=False)

        # Reorder columns
        tag_df = tag_df[["consequent_name", "antecedent_names", "post_count", "status"]]

    return tag_df


# Example usage
dbr_url = "https://danbooru.donmai.us/tag_implications.json?commit=Search&limit=1000"
df = get_dbr_jsons(dbr_url)

# Ensure post_count is an integer
df["post_count"] = df["post_count"].astype(int)

# Save DataFrame to CSV
output_file = os.path.join(script_dir, "sorted_tag_implications.csv")
df.to_csv(output_file, index=False, encoding="utf-8")
print(f"DataFrame saved to {output_file}")
