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

from global_defaults import DBR_ALIAS_URL, DBR_BASE_URL
from tag_lists.tag_list_utils import add_aliases

# todo: e621 category 5 is species while in dbr is meta tag

# region global vars

# TODO: make character/artist/copyright lists/wildcards
### TODO: make character list with gender sorting
### (involves scraping each character's first (few) posts to get gender tags)




# endregion


# region danbooru processing


def process_dbr_tags(settings):
    df1 = get_dbr_jsons(settings, DBR_BASE_URL)

    df1 = df1[df1["post_count"] >= settings["min_post_thresh"]]
    df1 = df1[["name", "category", "post_count"]]  # Switch 'category' and 'post_count' and remove useless columns
    df1 = df1.sort_values(by="post_count", ascending=False)

    if settings["incl_aliases"] == "y":  # NOTE: e621 has extra "pending" status for alias tags while danbooru does not
        df2 = get_dbr_jsons(settings, DBR_ALIAS_URL)

        if settings["dbr_incl_deleted_alias"] == "n":
            df2 = df2[df2["status"] == "active"]

        df2 = df2[["antecedent_name", "consequent_name"]]

        return add_aliases(df1, df2)

    else:
        return df1


def get_dbr_jsons(settings, dbr_url: str):
    """scrape tags and aliases from Danbooru jsons"""
    tag_df = pd.DataFrame()

    for page in range(1, 1001):
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
            for item in data:
                if int(item["post_count"]) < int(settings["min_post_thresh"]):
                    print(f"(DBR) Stopping early due to hitting minimum post threshold on page {page}...", flush=True)
                    return tag_df  # Return early if the condition is met
        else:
            print(f"(DBR) Page {page} aliases processed...", flush=True)
        time.sleep(0.3)  # Sleep for 0.3 second because i guess it helps with ratelimits?

    return tag_df


# endregion
