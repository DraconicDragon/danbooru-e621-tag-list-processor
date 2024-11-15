import gzip
import io
import os
import re
import time
from datetime import datetime
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

# region global vars

E621_BASE_URL = "https://e621.net/db_export/"  # come in csv format compressed in gz file

DBR_BASE_URL = "https://danbooru.donmai.us/tags.json?limit=1000&search[hide_empty]=yes&search[is_deprecated]=no&search[order]=count"  # 1000 is upper limit
DBR_ALIAS_URL = "https://danbooru.donmai.us/tag_aliases.json?commit=Search&limit=1000&search[order]=tag_count"  # 1000 is upper limit

DEFAULTS = {
    "choice_site": 3,
    "min_post_thresh": 50,
    "incl_aliases": "y",
    "dbr_incl_deleted_alias": "y",
    "e6_incl_pending_alias": "n",
    "e6_incl_deleted_alias": "y",
}

# get the current directory of the script to save csvs in same dir
current_directory = os.path.dirname(__file__)

# date in 'year_month_day' format, im pooping on both US and EU hieheheiheiheheie, jap. one fits better for this
current_date = datetime.now().strftime("%Y_%m_%d")

# endregion


# region main start + user input
# i fricking hate user input managing, i hate it so much, i hate it so much - i hate it so much - github copilot
# seriously tho if i didn't think of YOU, yes YOU, the "person" (assuming) that's reading this hot garbage, i wouldn't have done this
def get_input(prompt, default_value, cast_func=str):
    """Helper function to get input with a default value."""
    user_input = input(f"{prompt} (Default = {default_value}): ")
    if user_input == "":
        return default_value
    try:
        return cast_func(user_input)
    except ValueError:
        print(f"Invalid input. Using default: {default_value}")
        return default_value


def options():  # TODO: add option to change underscore to space although this isnt really needed as the extensions this is for do that by themselves
    print("To use the default of any option, just press enter.")
    choice_site = get_input(
        "Which site do you want to create a tag list from? (1|2|3)\n"
        + "(1) Danbooru\n"
        + "(2) e621\n"
        + "(3) Both, Creates a separate list for each site + a merged list",
        DEFAULTS["choice_site"],
        int,
    )
    min_post_thresh = get_input(
        "Enter min. number of posts for a tag to be kept (tags with fewer posts will be pruned)",
        DEFAULTS["min_post_thresh"],
        int,
    )
    incl_aliases = get_input("Do you want to include alias tags? (y/N)", DEFAULTS["incl_aliases"]).lower()

    if incl_aliases == "y":
        # Site-specific options
        # deleted has higher chance of having been trained by AI and pending is too recent/non existent
        dbr_incl_deleted_alias = "y"
        e6_incl_pending_alias = "n"
        e6_incl_deleted_alias = "y"

        if choice_site in (1, 3):
            dbr_incl_deleted_alias = get_input(
                "(DBR) Do you want to include alias tags that aren't in use by Danbooru anymore (deleted aliases)? (y/N)",
                DEFAULTS["dbr_incl_deleted_alias"],
            ).lower()

        if choice_site in (2, 3):
            e6_incl_pending_alias = get_input(
                "(E621) Do you want to include 'pending' alias tags? (y/N)", DEFAULTS["e6_incl_pending_alias"]
            ).lower()
            e6_incl_deleted_alias = get_input(
                "(E621) Do you want to include alias tags that aren't in use by e621 anymore (deleted aliases)? (y/N)",
                DEFAULTS["e6_incl_deleted_alias"],
            ).lower()
    else:
        dbr_incl_deleted_alias = "n"
        e6_incl_pending_alias = "n"
        e6_incl_deleted_alias = "n"

    return {
        "choice_site": choice_site,
        "min_post_thresh": min_post_thresh,
        "incl_aliases": incl_aliases,
        "dbr_incl_deleted_alias": dbr_incl_deleted_alias,
        "e6_incl_pending_alias": e6_incl_pending_alias,
        "e6_incl_deleted_alias": e6_incl_deleted_alias,
    }


def main():
    settings = options()

    df1 = pd.DataFrame()
    df2 = pd.DataFrame()

    if settings["choice_site"] == 1:
        df1 = process_dbr_tags(settings)
    elif settings["choice_site"] == 2:
        df2 = process_e6_tags_csv(settings)
    elif settings["choice_site"] == 3:
        df1 = process_dbr_tags(settings)
        df2 = process_e6_tags_csv(settings)

    if not df1.empty:
        save_df_as_csv(df1, file_name_prefix="DBR_tags")  # TODO: change naming depending on user choice maybe?
    if not df2.empty:
        save_df_as_csv(df2, file_name_prefix="E6_tags")
    if not df1.empty and not df2.empty:
        merge_dbr_e6_tags(df1, df2)


# endregion


# region danbooru processing


def process_dbr_tags(settings):
    df1 = get_dbr_jsons(DBR_BASE_URL)

    df1 = df1[df1["post_count"] >= settings["min_post_thresh"]]
    df1 = df1[["name", "category", "post_count"]]  # Switch 'category' and 'post_count' and remove useless columns
    df1 = df1.sort_values(by="post_count", ascending=False)

    if settings["incl_aliases"] == "y":  # NOTE: e621 has extra "pending" status for alias tags while danbooru does not
        df2 = get_dbr_jsons(DBR_ALIAS_URL)

        if settings["dbr_incl_deleted_alias"] == "n":
            df2 = df2[df2["status"] == "active"]

        df2 = df2[["antecedent_name", "consequent_name"]]

        return add_aliases(df1, df2)

    else:
        return df1


def get_dbr_jsons(dbr_url: str):
    """get tags and aliases from Danbooru jsons"""
    tag_df = pd.DataFrame()

    for page in range(1, 5):
        url = f"{dbr_url}&page={page}"  # Update URL with current page

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            if not data:  # Break the loop if the data is empty (no more tags to fetch)
                print(f"(DBR) No more data found at page {page}. Stopping...", flush=True)
                break

        tag_df = pd.concat([tag_df, pd.DataFrame(data)], ignore_index=True)

        if dbr_url == DBR_BASE_URL:
            print(f"(DBR) Page {page} tags processed...", flush=True)
        else:
            print(f"(DBR) Page {page} aliases processed...", flush=True)
        time.sleep(0.3)  # Sleep for 0.5 second because i guess it helps with ratelimits?

    # output_path = os.path.join(current_directory, f"DBR_aliases_{current_date}.csv")
    # tag_df.to_csv(output_path, index=False)
    # print(tag_df.head())  # Shows the first 5 rows

    return tag_df


# endregion


# region e621 processing


def process_e6_tags_csv(settings):
    """remove 'id' and 'created_at' column, sort by 'post_count', and filter 'post_count' >= 50"""

    latest_file_url = get_latest_file_url(E621_BASE_URL, alias_requested=False)
    unpacked_content = download_and_unpack_gz(latest_file_url)
    df = pd.read_csv(io.StringIO(unpacked_content))

    df = df[["name", "category", "post_count"]]
    df = df.sort_values(by="post_count", ascending=False)
    df = df[df["post_count"] >= settings["min_post_thresh"]]

    if settings["incl_aliases"] == "y":
        alias_df = process_e6_aliases_csv(settings, "tag_aliases-2024-11-14.csv")
        return add_aliases(df, alias_df)

    else:
        return df


def process_e6_aliases_csv(settings):
    """filter by 'status' == 'user choice' | then remove 'status' + 'id' + 'created_at' columns"""
    latest_file_url = get_latest_file_url(E621_BASE_URL, alias_requested=True)
    unpacked_content = download_and_unpack_gz(latest_file_url)
    df = pd.read_csv(io.StringIO(unpacked_content))

    if settings["e6_incl_deleted_alias"] == "n" and settings["e6_incl_pending_alias"] == "n":
        df = df[df["status"] == "active"]
    elif settings["e6_incl_deleted_alias"] == "n":
        df = df[df["status"] != "deleted"]
    elif settings["e6_incl_pending_alias"] == "n":
        df = df[df["status"] != "pending"]

    df = df[["antecedent_name", "consequent_name"]]

    # rows_with_na = df[df["antecedent_name"].isna()]
    # print(rows_with_na)

    return df


# region download e6 gz tag files


def get_latest_file_url(base_url, alias_requested: bool):
    # Fetch the page content
    response = requests.get(base_url)
    response.raise_for_status()  # Ensure successful response

    # Parse the page using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all links that might contain the date in the filename
    links = soup.find_all("a", href=True)

    # Regex to find dates in the filename
    if alias_requested:
        date_pattern = re.compile(r"tag_aliases-(\d{4}-\d{2}-\d{2})\.csv\.gz")
    else:
        date_pattern = re.compile(r"tags-(\d{4}-\d{2}-\d{2})\.csv\.gz")

    # Find the most recent date by extracting all matching dates
    latest_date = None
    latest_url = None
    for link in links:
        match = date_pattern.search(link["href"])
        if match:
            file_date = datetime.strptime(match.group(1), "%Y-%m-%d")
            if not latest_date or file_date > latest_date:
                latest_date = file_date
                latest_url = link["href"]

    # If a latest URL is found, construct the full download URL
    if latest_url:
        return urljoin(base_url, latest_url)
    else:
        raise ValueError("No valid file found on the page.")


def download_and_unpack_gz(url):
    print(f"(E621) Downloading file from {url}...")
    response = requests.get(url)
    response.raise_for_status()  # successful response insurance TM

    # Open .gz file in memory and unpack it in mem
    with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
        unpacked_data = f.read().decode("utf-8")

    return unpacked_data


# endregion

# endregion


# almost final step: helper function to add aliases for DBR and E621 dataframes
def add_aliases(df1: pd.DataFrame, df2: pd.DataFrame):  # df1 is tags, df2 is aliases
    """match consequent_name in df2 with names in df1, add aggregated antecedent_name as aliases in df1"""

    df2["antecedent_name"] = df2["antecedent_name"].fillna("").astype(str)  # f you e621 for having NaNs in your csvs

    aliases = df2.groupby("consequent_name")["antecedent_name"].apply(lambda x: ",".join(x)).reset_index()
    # expl so i don forge: group by cons_name, focus on ante_name, lambda to join all ante_names in their group (unique cons_name) with ','
    # reset index so it makes new dataframe in memory where its "comma,separate,string",cons_group_name/tag name

    df1 = df1.merge(
        aliases, how="left", left_on="name", right_on="consequent_name"
    )  # merge df1 with the "aliases" df created above
    df1["antecedent_name"] = df1["antecedent_name"].fillna("")  # fill NaN with empty string so below code works

    df1["aliases"] = ""  # make new 'aliases' column in df1
    # this basically checks if an antecedent_name exists for a tag, if it does, it adds it to the aliases
    df1["aliases"] = df1.apply(
        lambda row: row["aliases"] + row["antecedent_name"] if row["antecedent_name"] else row["aliases"], axis=1
    )

    df1 = df1.drop(
        columns=["consequent_name", "antecedent_name"]
    )  # removes the columns used from merge as they arent needed anymore
    return df1


# actual final step kinda
def merge_dbr_e6_tags(df1, df2):  # merge dbr and e6 tags by name and with both aliases
    # merge DataFrames on 'name'
    merged_df = pd.merge(df1, df2, on="name", how="outer", suffixes=("_df1", "_df2"))

    # Handle 'category': take the non-NaN value from either DataFrame and convert to int
    merged_df["category"] = merged_df["category_df1"].combine_first(merged_df["category_df2"]).astype(int)

    # Handle 'post_count': calculate a weighted average, round, and convert to int
    merged_df["post_count"] = (
        ((merged_df["post_count_df1"].fillna(0) + merged_df["post_count_df2"].fillna(0)) / 2).round().astype(int)
    )

    # Combine aliases, removing duplicates
    merged_df["aliases"] = merged_df["aliases_df1"].fillna("") + "," + merged_df["aliases_df2"].fillna("")
    merged_df["aliases"] = merged_df["aliases"].str.split(",").apply(lambda x: ",".join(sorted(set(x))))

    merged_df = merged_df.sort_values(by="post_count", ascending=False)

    # Keep only the necessary columns
    result = merged_df[["name", "category", "post_count", "aliases"]]

    save_df_as_csv(result, file_name_prefix="DBRE6_combi_tags")


def save_df_as_csv(df, file_name_prefix):
    output_path = os.path.join(current_directory, f"{file_name_prefix}_{current_date}.csv")
    df.to_csv(output_path, index=False)
    print(f"CSV file has been saved as '{output_path}'")


main()
