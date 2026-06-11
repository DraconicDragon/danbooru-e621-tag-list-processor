# region e621 processing

import gzip
import io

import pandas as pd
import requests

from defaults import E621_BASE_URL, E621_HEADERS
from tag_lists.merge_utils import add_aliases


def process_e621_tags_csv(settings):
    """Remove unused columns, sort by post_count, and filter by minimum post count."""
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

    df["aliases"] = ""
    return df


def process_e621_aliases_csv(settings):
    """Filter by status and keep only antecedent/consequent names."""
    latest_file_info = get_latest_e621_tags_file_info(E621_BASE_URL, target="aliases")
    unpacked_content = download_and_unpack_gz_memory(latest_file_info["url"])
    df = pd.read_csv(io.StringIO(unpacked_content))

    if settings["e6_incl_deleted_alias"] == "n" and settings["e6_incl_pending_alias"] == "n":
        df = df[df["status"] == "active"]
    elif settings["e6_incl_deleted_alias"] == "n":
        df = df[df["status"] != "deleted"]
    elif settings["e6_incl_pending_alias"] == "n":
        df = df[df["status"] != "pending"]

    return df[["antecedent_name", "consequent_name"]]


# region fetch e6 gz tag files


def get_latest_e621_tags_file_info(base_url, target: str):
    target_names = {
        "artists": "artists",
        "bulk_update_requests": "bulk_update_requests",
        "pools": "pools",
        "posts": "posts",
        "aliases": "tag_aliases",
        "implications": "tag_implications",
        "tags": "tags",
        "wiki_pages": "wiki_pages",
        "post_replacements": "post_replacements",
        "post_versions": "post_versions",
    }

    if target not in target_names:
        raise ValueError(f'Invalid target specified: "{target}". Valid targets are: {list(target_names.keys())}')

    response = requests.get(base_url, headers=E621_HEADERS)
    response.raise_for_status()

    exports = response.json()
    wanted_name = target_names[target]

    for export in exports:
        if export["name"] == wanted_name:
            updated_at = export["updated_at"]
            date_part, time_part = updated_at.split("T", 1)
            time_part = time_part.split(".", 1)[0].replace(":", "-")

            return {
                "url": export["url"],
                "filename": export["file_name"],
                "date": date_part,
                "time": time_part,
            }

    raise ValueError(f'No export found for target "{target}".')


def download_and_unpack_gz_memory(url):
    print(f"(E621) Downloading file from {url}...")
    response = requests.get(url, headers=E621_HEADERS)
    response.raise_for_status()

    with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
        unpacked_data = f.read().decode("utf-8")

    return unpacked_data
