import os
from datetime import datetime

import pandas as pd

from input_manager import options
from tag_lists.danbooru import process_dbr_tags
from tag_lists.e621 import process_e621_tags_csv
from tag_lists.merge_utils import (
    merge_dbr_e6_tags,
    remove_useless_tags,
    sanitize_aliases_merged,
)

# get the current directory of the script to save csvs in same dir
current_directory = os.path.dirname(__file__)

# date in 'year-month-day' format, im pooping on both US and EU hieheheiheiheheie, jap. one fits better for this
current_date = datetime.now().strftime("%Y-%m-%d")


def save_df_as_csv(df, filename_prefix, filename_suffix):
    output_folder = os.path.join(current_directory, "tag_lists_output")

    # Create the folder if it doesn't exist, exist_ok=True prevent error if already exists
    os.makedirs(output_folder, exist_ok=True)

    # todo: handle existing csv, if exist with same settings, try tow ork with that, or skip
    output_path = os.path.join(output_folder, f"{filename_prefix}_{current_date}_{filename_suffix}.csv")
    df.to_csv(output_path, index=False, header=False)
    print(f"CSV file has been saved as '{output_path}'")


def save_krita_csv(df, is_e621_df):
    output_folder = os.path.join(current_directory, "tag_lists_output", "krita_ai_compatible")

    # Create the folder if it doesn't exist, exist_ok=True prevent error if already exists
    os.makedirs(output_folder, exist_ok=True)

    if is_e621_df:
        output_path = os.path.join(output_folder, f"e621 NSFW.csv")
    else:
        output_path = os.path.join(output_folder, f"Danbooru NSFW.csv")

    df.to_csv(output_path, index=False, header=True)
    print(f"Krita Compatible CSV file has been saved as '{output_path}'")


def main():
    settings = options()

    fn_suffix = (
        f"pt{settings['min_post_thresh']}-"  # create file name suffix based on settings
        f"{'ia-' if settings['incl_aliases'] == 'y' else ''}"  # include 'ia-' if the setting is 'y'
        + (  # include the following only if 'incl_aliases' is 'y'
            f"{'dd-' if settings['dbr_incl_deleted_alias'] == 'y' else ''}"
            f"{'ep-' if settings['e6_incl_pending_alias'] == 'y' else ''}"
            f"{'ed-' if settings['e6_incl_deleted_alias'] == 'y' else ''}"
            if settings["incl_aliases"] == "y"  # if is here
            else ""
        )
    )
    # todo: remove ep/ed/dd depending on which file; actually isnt this completely broken?
    # overcomplicated garbage i forgot how it does things anyway but too lazy to rewrite rn
    # wait nvm its working
    fn_suffix = fn_suffix.rstrip("-")

    dbr_df, e621_df = pd.DataFrame(), pd.DataFrame()

    if settings["choice_site"] == 1:
        dbr_df = process_dbr_tags(settings)
    elif settings["choice_site"] == 2:
        e621_df = process_e621_tags_csv(settings)
    elif settings["choice_site"] == 3:
        dbr_df = process_dbr_tags(settings)
        e621_df = process_e621_tags_csv(settings)

    if not dbr_df.empty:
        dbr_df = remove_useless_tags(dbr_df)  # clean unneeded tags
        save_df_as_csv(dbr_df, filename_prefix="danbooru", filename_suffix=fn_suffix)
    if not e621_df.empty:
        e621_df = remove_useless_tags(e621_df)  # clean unneeded tags
        save_df_as_csv(e621_df, filename_prefix="e621", filename_suffix=fn_suffix)
    if not dbr_df.empty and not e621_df.empty:
        merged_df = merge_dbr_e6_tags(dbr_df, e621_df)
        merged_df = sanitize_aliases_merged(merged_df)  # clean aliases so autocompletes dont reference wrong tags
        save_df_as_csv(merged_df, filename_prefix="danbooru_e621_merged", filename_suffix=fn_suffix)

    if settings["create_krita_csv"] == "y":
        if not dbr_df.empty:
            save_krita_csv(dbr_df, is_e621_df=False)
        if not e621_df.empty:
            save_krita_csv(e621_df, is_e621_df=True)


if __name__ == "__main__":
    main()
