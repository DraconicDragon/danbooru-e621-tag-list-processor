import os
from datetime import datetime

import pandas as pd

from input_manager import options
from modules.danbooru_scrape import process_dbr_tags
from modules.e621_scrape import process_e621_tags_csv
from modules.merge_utils import (
    merge_dbr_e6_tags,
    remove_useless_tags,
    sanitize_aliases_merged,
)
from raw_data_scrape.main_raw import do_thing

# get the current directory of the script to save csvs in same dir
current_directory = os.path.dirname(__file__)

# date in 'year-month-day' format, im pooping on both US and EU hieheheiheiheheie, jap. one fits better for this
current_date = datetime.now().strftime("%Y-%m-%d")


def save_df_as_csv(df, filename_prefix, filename_suffix):
    output_folder = os.path.join(current_directory, "output", "tag_lists")

    # Create the folder if it doesn't exist, exist_ok=True prevent error if already exists
    os.makedirs(output_folder, exist_ok=True)

    # todo: handle existing csv, if exist with same settings, try tow ork with that, or skip
    output_path = os.path.join(output_folder, f"{filename_prefix}_{current_date}_{filename_suffix}.csv")
    df.to_csv(output_path, index=False, header=False)
    print(f"CSV file has been saved as '{output_path}'")


def save_krita_csv(df, is_e621_df):
    output_folder = os.path.join(current_directory, "output", "tag_lists", "krita_ai_compatible")

    # Create the folder if it doesn't exist, exist_ok=True prevent error if already exists
    os.makedirs(output_folder, exist_ok=True)

    df.columns = ["tag", "type", "count", "aliases"]
    df = df[(df["type"] != 6) & (df["type"] != 7) & (df["type"] != 8)]

    if is_e621_df:
        output_path = os.path.join(output_folder, f"e621 NSFW.csv")
    else:
        output_path = os.path.join(output_folder, f"Danbooru NSFW.csv")

    df.to_csv(output_path, index=False, header=True)
    print(f"Krita Compatible CSV file has been saved as '{output_path}'")


def main():
    settings = options()

    if settings["option_type"] == "raw":
        do_thing(settings)
        return

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
        # merged post count type
        + f"{'dpc-' if settings['merged_post_count_type'] == 1 else ''}"  # Danbooru
        + f"{'epc-' if settings['merged_post_count_type'] == 2 else ''}"  # e621
        + f"{'spc-' if settings['merged_post_count_type'] == 3 else ''}"  # Sum of Both
    )
    fn_suffix = fn_suffix.rstrip("-")

    def adjust_suffix(original_suffix, parts_to_remove):
        parts = original_suffix.split("-")
        filtered = [part for part in parts if part not in parts_to_remove]
        adjusted = "-".join(filtered)
        return adjusted.rstrip("-")

    dbr_df, e621_df = pd.DataFrame(), pd.DataFrame()

    # processing
    if settings["choice_site"] == 1:
        dbr_df = process_dbr_tags(settings)
    elif settings["choice_site"] == 2:
        e621_df = process_e621_tags_csv(settings)
    elif settings["choice_site"] == 3:
        dbr_df = process_dbr_tags(settings)
        e621_df = process_e621_tags_csv(settings)

    # saving
    if not dbr_df.empty:
        dbr_df = remove_useless_tags(dbr_df)  # clean unneeded tags
        dbr_suffix = adjust_suffix(fn_suffix, ["ep", "ed", "dpc", "epc", "spc"])
        save_df_as_csv(dbr_df, filename_prefix="danbooru", filename_suffix=dbr_suffix)

    if not e621_df.empty:
        e621_df = remove_useless_tags(e621_df)  # clean unneeded tags
        e6_suffix = adjust_suffix(fn_suffix, ["dd", "dpc", "epc", "spc"])
        save_df_as_csv(e621_df, filename_prefix="e621", filename_suffix=e6_suffix)

    if not dbr_df.empty and not e621_df.empty:
        merged_df = merge_dbr_e6_tags(dbr_df, e621_df, settings["merged_post_count_type"])
        merged_df = sanitize_aliases_merged(merged_df)  # clean aliases so autocompletes dont reference wrong tags
        save_df_as_csv(merged_df, filename_prefix="danbooru_e621_merged", filename_suffix=fn_suffix)

    if settings["create_krita_csv"] == "y":
        if not dbr_df.empty:
            save_krita_csv(dbr_df, is_e621_df=False)
        if not e621_df.empty:
            save_krita_csv(e621_df, is_e621_df=True)


if __name__ == "__main__":
    main()
