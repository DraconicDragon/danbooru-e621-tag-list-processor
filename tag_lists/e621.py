# region e621 processing

import gzip
import io
import re
from datetime import datetime
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

from global_defaults import E621_BASE_URL
from tag_lists.merge_utils import add_aliases


def process_e621_tags_csv(settings):
    """remove 'id' and 'created_at' column, sort by 'post_count', and filter 'post_count' >= 50"""

    latest_file_url = get_latest_e621_tags_file_url(E621_BASE_URL, alias_requested=False)
    unpacked_content = download_and_unpack_gz_memory(latest_file_url)
    df = pd.read_csv(io.StringIO(unpacked_content))

    df = df[["name", "category", "post_count"]]
    df = df[df["category"] != 6]  # invalid tags, disambiguation
    df = df.sort_values(by="post_count", ascending=False)
    df = df[df["post_count"] >= settings["min_post_thresh"]]

    if settings["incl_aliases"] == "y":
        alias_df = process_e621_aliases_csv(settings)
        return add_aliases(df, alias_df)

    else:
        return df


# todo: cache the gz files maybe
def process_e621_aliases_csv(settings):
    """filter by 'status' == 'user choice' | then remove 'status' + 'id' + 'created_at' columns"""
    latest_file_url = get_latest_e621_tags_file_url(E621_BASE_URL, alias_requested=True)
    unpacked_content = download_and_unpack_gz_memory(latest_file_url)
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


def get_latest_e621_tags_file_url(base_url, alias_requested: bool):
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
