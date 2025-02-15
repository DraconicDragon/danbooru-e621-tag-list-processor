# almost final step: helper function to add aliases for DBR and E621 dataframes
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


def merge_dbr_e6_tags(dbr_df, e621_df):
    # distinct categories for e621 for the merged df/csv (related: sd webui tagcomplete repo implementation of merged list)
    e621_df["category"] += 7

    # print the first 10 rows of the dfs
    # print(dbr_df.head(10))
    # print(e621_df.head(10))
    # return None

    merged_df = pd.concat([dbr_df, e621_df], ignore_index=True)

    # merges both DFs and takes the first df's (danbooru) value if the same tag exists across two DFs to
    # prevent autocomplete from getting confused which tag to use
    ###
    # Group by the name column (index 0) and aggregate
    # category and post_count column values (index 1 and 2) are taken from dbr_df
    # aliases column (index 3) is a concatenation of unique values only from both (concat aliases)
    result_df = merged_df.groupby("name", as_index=False).agg(
        {
            "category": "first",  # Take the first value (from danbooru)
            "post_count": "first",  # Take the first value (from danbooru)
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


# todo: IMPORTANT: REWORK, IGNORE BOTTOM CODE
# actual final step kinda#
# TODO: USE E621 HIGHER CATEGORY CSV/DATAFRAME TO MERGE WITH DBR TAGS; sd webui tagcomplete compat + cleaner
def merge_dbr_e6_tags_old(df1, df2):  # merge dbr and e6 tags by name and with both aliases
    # merge DataFrames on 'name'
    merged_df = pd.merge(df1, df2, on="name", how="outer", suffixes=("_df1", "_df2"))

    # Handle 'category': take the non-NaN value from either DataFrame and convert to int
    merged_df["category"] = merged_df["category_df1"].combine_first(merged_df["category_df2"]).astype(int)

    # Handle 'post_count': round numbers, and convert to int
    merged_df["post_count"] = (
        (merged_df["post_count_df1"].fillna(0) + merged_df["post_count_df2"].fillna(0)).round().astype(int)
    )

    # Handle 'aliases' column safely
    if "aliases_df1" in merged_df.columns or "aliases_df2" in merged_df.columns:
        # Combine aliases from both DataFrames if they exist
        aliases_df1 = merged_df["aliases_df1"].fillna("") if "aliases_df1" in merged_df.columns else ""
        aliases_df2 = merged_df["aliases_df2"].fillna("") if "aliases_df2" in merged_df.columns else ""
        merged_df["aliases"] = aliases_df1 + "," + aliases_df2
        # Remove duplicates, trailing commas, and sort the aliases
        merged_df["aliases"] = (
            merged_df["aliases"]
            .str.split(",")
            .apply(lambda x: ",".join(sorted(set(filter(None, x)))))  # Remove empty strings and duplicates
        )
    else:
        # Remove the aliases column entirely if neither DataFrame has it
        merged_df = merged_df.drop(columns=["aliases_df1", "aliases_df2"], errors="ignore")

    # Sort by 'post_count' descending
    merged_df = merged_df.sort_values(by="post_count", ascending=False)

    # keep only the necessary columns
    columns_to_keep = ["name", "category", "post_count"]
    if "aliases" in merged_df.columns:
        columns_to_keep.append("aliases")
    result = merged_df[columns_to_keep]

    return result


def remove_useless_tags():  # TODO: implement this; its clean_useless_tags.py; import from there soon:TM:?
    """remove tags that are basically meta tags, like 'bad_pixiv_id' or 'conditional dnp'"""
    pass
