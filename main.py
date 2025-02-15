import os
from datetime import datetime

import pandas as pd

from input_manager import options
from tag_lists.danbooru import process_dbr_tags
from tag_lists.e621 import process_e621_tags_csv
from tag_lists.tag_list_utils import merge_dbr_e6_tags

# get the current directory of the script to save csvs in same dir
current_directory = os.path.dirname(__file__)

# date in 'year-month-day' format, im pooping on both US and EU hieheheiheiheheie, jap. one fits better for this
current_date = datetime.now().strftime("%Y-%m-%d")


def save_df_as_csv(df, filename_prefix, filename_suffix):
    output_path = os.path.join(current_directory, f"zlists/{filename_prefix}_{current_date}_{filename_suffix}.csv")
    df.to_csv(output_path, index=False, header=False)
    print(f"CSV file has been saved as '{output_path}'")


def main():
    settings = options()

    dbr_df, e621_df = pd.DataFrame(), pd.DataFrame()

    if settings["choice_site"] == 1:
        dbr_df = process_dbr_tags(settings)
    elif settings["choice_site"] == 2:
        e621_df = process_e621_tags_csv(settings)
    elif settings["choice_site"] == 3:
        dbr_df = process_dbr_tags(settings)
        e621_df = process_e621_tags_csv(settings)

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
    )  # todo: remove ep/ed/dd depending on which file
    fn_suffix = fn_suffix.rstrip("-")

    if not dbr_df.empty:
        save_df_as_csv(dbr_df, filename_prefix="danbooru_tags", filename_suffix=fn_suffix)
    if not e621_df.empty:
        save_df_as_csv(e621_df, filename_prefix="e621_tags", filename_suffix=fn_suffix)
    if not dbr_df.empty and not e621_df.empty:
        merged_list = merge_dbr_e6_tags(dbr_df, e621_df)
        save_df_as_csv(merged_list, filename_prefix="DBRE6_merged_tags", filename_suffix=fn_suffix)


if __name__ == "__main__":
    main()
