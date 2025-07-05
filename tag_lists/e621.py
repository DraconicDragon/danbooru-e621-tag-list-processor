# region e621 processing

import gzip
import io
import re
from datetime import datetime
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

from defaults import E621_BASE_URL
from tag_lists.merge_utils import add_aliases


def process_e621_tags_csv(settings):
    """remove 'id' and 'created_at' column, sort by 'post_count', and filter 'post_count' >= 50"""

    latest_file_info = get_latest_e621_tags_file_info(E621_BASE_URL, target="tags")
    unpacked_content = download_and_unpack_gz_memory(latest_file_info["url"])
    df = pd.read_csv(io.StringIO(unpacked_content))

    df = df[["name", "category", "post_count"]]
    df = df[df["category"] != 6]  # invalid tags, disambiguation
    df = df.sort_values(by="post_count", ascending=False)
    df = df[df["post_count"] >= settings["min_post_thresh"]]

    if settings["incl_aliases"] == "y":
        alias_df = process_e621_aliases_csv(settings)
        return add_aliases(df, alias_df)

    else:
        df["aliases"] = ""
        return df


# todo: cache the gz files maybe
def process_e621_aliases_csv(settings):
    """filter by 'status' == 'user choice' | then remove 'status' + 'id' + 'created_at' columns"""
    latest_file_info = get_latest_e621_tags_file_info(E621_BASE_URL, target="aliases")
    unpacked_content = download_and_unpack_gz_memory(latest_file_info["url"])
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


# region fetch e6 gz tag files


def get_latest_e621_tags_file_info(base_url, target: str):
    # Define the patterns for different target files
    target_patterns = {
        "pools": r"(pools-(\d{4}-\d{2}-\d{2})\.csv\.gz)",
        "posts": r"(posts-(\d{4}-\d{2}-\d{2})\.csv\.gz)",
        "aliases": r"(tag_aliases-(\d{4}-\d{2}-\d{2})\.csv\.gz)",
        "implications": r"(tag_implications-(\d{4}-\d{2}-\d{2})\.csv\.gz)",
        "tags": r"(tags-(\d{4}-\d{2}-\d{2})\.csv\.gz)",
        "wiki_pages": r"(wiki_pages-(\d{4}-\d{2}-\d{2})\.csv\.gz)",
    }

    if target not in target_patterns:
        raise ValueError(f'Invalid target specified: "{target}". Valid targets are: {list(target_patterns.keys())}')

    # Fetch the page content
    response = requests.get(base_url)
    response.raise_for_status()  # Ensure successful response

    # Parse the page using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")
    pre = soup.find("pre")

    if not pre:
        raise RuntimeError("Could not find <pre> block in HTML.")

    lines = pre.text.splitlines()
    pattern = re.compile(target_patterns[target])

    latest_date = None
    latest_info = None

    for line in lines:
        match = pattern.search(line)
        if match:
            filename = match.group(1)
            date_str = match.group(2)

            # Extract the time (e.g., "07:44") from the line using a second regex
            time_match = re.search(r"\b(\d{2}:\d{2})\b", line)
            file_time = time_match.group(1) if time_match else None
            file_time = file_time.replace(":", "-")  # type:ignore

            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            if not latest_date or file_date > latest_date:
                latest_date = file_date
                latest_info = {
                    "url": urljoin(base_url, filename),
                    "filename": filename,
                    "date": date_str,
                    "time": file_time,
                }

    if latest_info:
        return latest_info
    else:
        raise ValueError("No valid file found on the page.")


def download_and_unpack_gz_memory(url):
    print(f"(E621) Downloading file from {url}...")
    response = requests.get(url)
    response.raise_for_status()  # successful response insurance TM

    # Open .gz file in memory and unpack it in mem
    with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
        unpacked_data = f.read().decode("utf-8")

    return unpacked_data


# endregion

# endregion
