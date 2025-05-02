# almost final step: helper function to add aliases for DBR and E621 dataframes
import json
import os

import pandas as pd


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


def merge_dbr_e6_tags(dbr_df, e621_df, merged_post_count_type):
    # prevent modification of original DataFrame
    e621_df = e621_df.copy()

    # distinct categories for e621 for the merged df/csv (related: sd webui tagcomplete repo implementation of merged list)
    e621_df["category"] += 7

    # print the first 10 rows of the dfs
    # print(dbr_df.head(10))
    # print(e621_df.head(10))
    # return None

    merged_df = pd.concat([dbr_df, e621_df], ignore_index=True)

    # Determine the aggregation function for post_count based on merged_post_count_type
    if merged_post_count_type == 1:
        post_count_agg = "first"  # Take the first value (from danbooru)
    elif merged_post_count_type == 2:
        post_count_agg = lambda x: x.iloc[1] if len(x) > 1 else x.iloc[0]  # Take the second value (from e621)
    elif merged_post_count_type == 3:
        post_count_agg = "sum"  # sum of both post counts (danbooru + e621)
    else:
        raise ValueError(f"Invalid merged_post_count_type. merged_post_count_type: {merged_post_count_type}")

    # merges both DFs and takes the first df's (danbooru) value if the same tag exists across two DFs to
    # prevent autocomplete from getting confused which tag to use
    ###
    # Group by the name column (index 0) and aggregate
    # category and post_count column values (index 1 and 2) are taken from dbr_df
    # aliases column (index 3) is a concatenation of unique values only from both (concat aliases)
    result_df = merged_df.groupby("name", as_index=False).agg(
        {
            "category": "first",  # Take the first value (from danbooru)
            "post_count": post_count_agg,
            "aliases": lambda x: ",".join(
                sorted(
                    set(
                        [
                            item.strip() for val in x.dropna() for item in val.split(",") if item.strip()
                        ]  # Flatten and deduplicate
                    )
                )
            ),  # Merge unique, non-NaN strings and remove duplicates
        }
    )

    # Sort the result by the third column (index 2) in descending order (sort by post count)
    result_df = result_df.sort_values(by="post_count", ascending=False)
    return result_df


def remove_useless_tags(df):
    """remove tags that are basically meta tags, like 'bad_pixiv_id' or 'conditional dnp'"""

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the blacklisted_tags.json file
    blacklisted_tags_file = os.path.abspath(os.path.join(script_dir, "..", "blacklisted_tags.json"))

    with open(blacklisted_tags_file, "r") as f:
        blacklisted_tags_data = json.load(f)

    # Combine all blacklisted tags from both categories into a single list
    blacklisted_tags = blacklisted_tags_data.get("dbr", []) + blacklisted_tags_data.get("e621", [])

    # Filter out rows that contain blacklisted tags
    df = df[~df["name"].isin(blacklisted_tags)]
    return df


def sanitize_aliases_merged(df):
    "removes aliases that exist as normal tags in name column"
    df["aliases"] = df["aliases"].fillna("")

    # get all tags from column 1 into a set
    all_tags = set(df["name"].str.strip())

    def remove_duplicate_tags(row):
        tags = row["aliases"].strip()

        if not tags:  # skip empty tags
            return tags

        # split the aliases into list, strip spaces, remove any alias tag that already appears in column 1
        tag_list = [tag.strip() for tag in tags.split(",")]
        filtered_tags = [tag for tag in tag_list if tag not in all_tags]

        return ",".join(filtered_tags)

    # start filter column 4
    df["aliases"] = df.apply(remove_duplicate_tags, axis=1)

    return df
