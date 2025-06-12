from defaults import DBR_SCRAPE_TARGETS, DEFAULTS, E6_SCRAPE_TARGETS


def int_list(user_input):
    """Convert a comma-separated string into a list of ints.
    Example: '1,3,19' -> [1, 3, 19]"""
    try:
        # Split the input by commas, strip whitespace, and convert each to int.
        original_list = [int(x.strip()) for x in user_input.split(",") if x.strip() != ""]

        seen = set()
        deduped_list = [x for x in original_list if not (x in seen or seen.add(x))]
        return sorted(deduped_list)

    except ValueError as e:
        raise ValueError("One or more inputs could not be converted to an integer.") from e


def confirm():
    user_input = input("Do you want to continue? (y/N): ").lower()
    if user_input in ("", "y", "ye", "yes", "1", "true"):
        return True
    else:
        print("Denied or Invalid input, asking again...")
        return False


def get_input(prompt, default_value, cast_func=str):
    """Helper function to get input with a default value."""
    user_input = input(f"\n{prompt}\n(Default = {default_value}): ").lower()

    if user_input == "":
        return default_value
    if user_input == "raw":
        return "raw"

    try:
        return cast_func(user_input)
    except ValueError:
        print(f"Invalid input. Using default: {default_value}")
        return default_value


def create_prompt(targets):
    top_entries, other_entries = [], []
    for key in sorted(targets.keys()):
        entry = targets[key]
        # Build a line with the key, name, and note (if any)
        line = f"({key}) {entry['name']}"
        if entry.get("note"):
            line += f" {entry['note']}"
        # Separate the entries into suggested (top) and others.
        if entry.get("suggested"):
            top_entries.append(line)
        else:
            other_entries.append(line)
    return top_entries, other_entries


def raw_options():
    print(
        "\n\nNOTE: You entered 'raw'-mode. In this mode you will not be able to create any tag lists.\n"
        + "Instead, this mode is used to scrape the raw data from the sites and save it as such"
        + "(E.g.: as JSON files like tag_implications.json for Danbooru). Raw mode does *not* (i think) download any images however the files may contain links to them"
    )
    print("To use the default value of any option, just press enter.")

    r_choice_site = get_input(
        "(RAW) Which site do you want to scrape from? (1|2|3)\n" + "(1) Danbooru\n" + "(2) e621\n" + "(3) Both",
        2,  # NOTE: e621 is default for raw because danbooru takes very long to scrape
        int,
    )

    if r_choice_site == "raw":
        r_choice_site = 2
        print("stoobid. \n using default value...")

    if r_choice_site in (1, 3):
        top_entries, other_entries = create_prompt(DBR_SCRAPE_TARGETS)
        dbr_scrape_choice_confirmed = False

        while not dbr_scrape_choice_confirmed:
            dbr_scrape_selection = get_input(
                "(RAW-DBR) What would you like to scrape? (Note: Danbooru data comes in JSON format.)\n"
                + "\n".join(top_entries)
                + "\n\nBelow are some more options, however they may not be useful in comparison to the above.\n"
                + "\n".join(other_entries)
                + "\n"
                + "This option allows selecting multiple options at once. E.g.: '1,3' for Tags and Implications.",
                [1, 2],
                int_list,
            )
            # Check if any selected number is higher than the maximum key in DBR_SCRAPE_TARGETS
            max_key = max(DBR_SCRAPE_TARGETS.keys())
            invalid_numbers = [num for num in dbr_scrape_selection if num > max_key]

            if invalid_numbers:
                print(f"Invalid selection: {invalid_numbers}. Please choose numbers up to {max_key}.")
                continue  # Skip confirmation and ask again

            print("(RAW-DBR) You selected: ", dbr_scrape_selection)
            dbr_scrape_choice_confirmed = confirm()
    else:
        dbr_scrape_selection = []

    if r_choice_site in (2, 3):
        top_entries, other_entries = create_prompt(E6_SCRAPE_TARGETS)
        e6_scrape_choice_confirmed = False

        while not e6_scrape_choice_confirmed:
            e6_scrape_selection = get_input(
                "(RAW-E621) What would you like to scrape? (Note: E621 data comes in CSV format.)\n"
                + "\n".join(top_entries)
                + "\n\nBelow are some more options, however they may not be useful in comparison to the above.\n"
                + "\n".join(other_entries)
                + "\n"
                + "This option allows selecting multiple options at once. E.g.: '1,3' for Tags and Implications.",
                [1, 2],
                int_list,
            )
            # Check if any selected number is higher than the maximum key in DBR_SCRAPE_TARGETS
            max_key = max(E6_SCRAPE_TARGETS.keys())
            invalid_numbers = [num for num in dbr_scrape_selection if num > max_key]

            if invalid_numbers:
                print(f"Invalid selection: {invalid_numbers}. Please choose numbers up to {max_key}.")
                continue  # Skip confirmation and ask again

            print("(RAW-E621) You selected: ", e6_scrape_selection)
            e6_scrape_choice_confirmed = confirm()
    else:
        e6_scrape_selection = []

    return {
        "option_type": "raw",
        "r_choice_site": r_choice_site,
        "dbr_scrape_selection": dbr_scrape_selection,
        "e6_scrape_selection": e6_scrape_selection,
    }


# todo: add option to remove contributors category (index 9?)
def options():
    print("To use the default value of any option, just press enter.")

    # region tag options
    choice_site = get_input(
        "Which site do you want to create a tag list from? (1|2|3)\n"
        + "(1) Danbooru\n"
        + "(2) e621\n"
        + "(3) Both, Creates a separate list for each site + a merged list",
        DEFAULTS["choice_site"],
        int,
    )

    # if choice_site == "raw" then stop this function immediately and run raw_options() instead
    if choice_site == "raw":
        return raw_options()

    if choice_site == 3:
        merge_method = get_input(
            "Regarding the merged list, which merging method do you want to use? (1|2|3)\n"
            + "(1) Old method - Simply increases each category number from e621 csv by 7.\n"
            + (
                "(2) New method - more future proof but current autocomplete programs don't support this as of 6th June 2025" 
                "- creates Separate column for 'services'; E.g.: the merged CSV will end up with an added column " 
                "which will have a string of comma-separated names of the 'services' the tag belongs to/shows up in like " 
                "tag_n,category_id,post_count,\"alias_1,alias_2\",\"danbooru,e621\" or just ...,\"danbooru\"\n"
            ),
            DEFAULTS["merge_method"],
            int,
        )
    else:
        merge_method = DEFAULTS["merge_method"]

    if choice_site == 3:
        merged_post_count_type = get_input(
            "Regarding the merged list, which type of post count should be used for tags? (1|2|3)\n"
            + "(1) Danbooru\n"
            + "(2) e621\n"
            + "(3) Sum of both, the post count from both sites will be added together.",
            DEFAULTS["merged_post_count_type"],
            int,
        )
    else:
        merged_post_count_type = DEFAULTS["merged_post_count_type"]

    min_post_thresh = get_input(
        "Enter min. number of posts for a tag to be kept (tags with fewer posts will be ignored)",
        DEFAULTS["min_post_thresh"],
        int,
    )
    incl_aliases = get_input(
        "Do you want to include alias tags? (y/N)",
        DEFAULTS["incl_aliases"],
        str,
    )

    if incl_aliases == "y":
        # Site-specific options
        # deleted aliases are tags that are no longer in use by the site but might be useful for autocomplete
        dbr_incl_deleted_alias = DEFAULTS["dbr_incl_deleted_alias"]
        e6_incl_pending_alias = DEFAULTS["e6_incl_pending_alias"]
        e6_incl_deleted_alias = DEFAULTS["e6_incl_deleted_alias"]

        if choice_site in (1, 3):
            dbr_incl_deleted_alias = get_input(
                "(DBR) Do you want to include alias tags that aren't in use by Danbooru anymore (deleted aliases)? (y/N)",
                DEFAULTS["dbr_incl_deleted_alias"],
            )

        if choice_site in (2, 3):
            e6_incl_pending_alias = get_input(
                "(E621) Do you want to include 'pending' alias tags? (y/N)", DEFAULTS["e6_incl_pending_alias"]
            )
            e6_incl_deleted_alias = get_input(
                "(E621) Do you want to include alias tags that aren't in use by e621 anymore (deleted aliases)? (y/N)",
                DEFAULTS["e6_incl_deleted_alias"],
            )
    else:
        dbr_incl_deleted_alias = "n"
        e6_incl_pending_alias = "n"
        e6_incl_deleted_alias = "n"

    create_krita_csv = get_input(
        "(KRITA) Do you want to create Krita AI compatible CSV files? (y/N)",
        DEFAULTS["create_krita_csv"],
        str,
    )

    # endregion

    # region wildcard options
    # create_wildcard = get_input(
    #     "Which site do you want to create a wildcard from? (1|2|3|4)\n"
    #     + "(1) Danbooru\n"
    #     + "(2) e621\n"
    #     + "(3) Both | Creates a separate list for each site + a merged list\n"
    #     + "(4) None | Do not create this",
    #     DEFAULTS["create_wildcard"],
    #     int,
    # )
    # # if selection is not 4 then ask what type of wildcard should be created (artist, character, series)
    # if create_wildcard != 4:
    #     wildcard_categories = (
    #         get_input(
    #             "Which category do you want to create a wildcard from? (comma-separated multi option)\n"
    #             + "(1) Artist names\n"
    #             + "(2) Character names\n"
    #             + "(3) Copyright/Franchise names\n"
    #             + "Separate your options by a comma. E.g.: '1,2,3' for all categories.",
    #             DEFAULTS["wildcard_categories"],
    #             str,
    #         )
    #         .replace(" ", "")
    #     )
    #     wildcard_categories = [int(item) for item in wildcard_categories.split(",")]  # example: [1,3] | [1,2,3]
    #     if 2 in wildcard_categories:
    #         print("WIP ignore; Do you want to sort the character names by gender (female/male)")
    # else:
    #     wildcard_categories = DEFAULTS["wildcard_categories"]
    # endregion

    # TODO: custom suffix?, custom filename?

    return {
        "option_type": "normal",
        "choice_site": choice_site,
        "merge_method": merge_method,
        "merged_post_count_type": merged_post_count_type,
        "min_post_thresh": min_post_thresh,
        "incl_aliases": incl_aliases,
        "dbr_incl_deleted_alias": dbr_incl_deleted_alias,
        "e6_incl_pending_alias": e6_incl_pending_alias,
        "e6_incl_deleted_alias": e6_incl_deleted_alias,
        "create_krita_csv": create_krita_csv,
        # "create_wildcard": create_wildcard,
        # "wildcard_categories": wildcard_categories,
    }
