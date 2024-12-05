import re

import pandas as pd

# todo: rename function as it should only remove categories
def create_wildcard_from_tags(tags_df: pd.DataFrame, categories: list,  post_count_thresh: int) -> str: # todo: change for yaml compat
    """Takes DataFrame and creates a newline separated artist/selected category only string"""

    if categories.__len__() > 1:
        raise NotImplementedError("Currently only one category is supported")

    # [0,1,2,3,4,5] | 0: General, 1: Artist, 2: unkown?, 3: Copyright, 4: Character, 5: Meta
    # remove every row where 'category' is not "1" (artists) and 'count' is below set number 100
    for category in categories:
        filtered_df = tags_df[(tags_df["category"] == int(category)) & (tags_df["count"] >= post_count_thresh)]


        # todo: dont delete count, use count to return as yaml
        # remove 'category', 'count', and 'aliases' columns
        filtered_df = filtered_df.drop(columns=["category", "count", "aliases"], errors="ignore")

        # string replacement and regex on remaining tag column # todo: improve this, its only one column
        for col in filtered_df.columns:
            filtered_df[col] = filtered_df[col].astype(str)  # ensure data is treated as strings
            filtered_df[col] = filtered_df[col].str.replace("_", " ", regex=False)  # remove underscores

            # escape parentheses | replace ( and ) with \( and \)
            filtered_df[col] = filtered_df[col].apply(lambda x: re.sub(r"([\(\)])", r"\\\1", x))

    return filtered_df.to_string(index=False) # currently only outputs simple text file
