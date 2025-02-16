from global_defaults import DEFAULTS


def get_input(prompt, default_value, cast_func=str):
    """Helper function to get input with a default value."""
    user_input = input(f"\n{prompt}\n(Default = {default_value}): ")
    if user_input == "":
        return default_value
    try:
        return cast_func(user_input)
    except ValueError:
        print(f"Invalid input. Using default: {default_value}")
        return default_value


# todo: add option to remove contributors category (index 9?)
def options():
    print("To use the default of any option, just press enter.")

    # region tag options
    choice_site = get_input(
        "Which site do you want to create a tag list from? (1|2|3)\n"
        + "(1) Danbooru\n"
        + "(2) e621\n"
        + "(3) Both, Creates a separate list for each site + a merged list",
        DEFAULTS["choice_site"],
        int,
    )
    min_post_thresh = get_input(
        "Enter min. number of posts for a tag to be kept (tags with fewer posts will be pruned)",
        DEFAULTS["min_post_thresh"],
        int,
    )
    incl_aliases = get_input("Do you want to include alias tags? (y/N)", DEFAULTS["incl_aliases"]).lower()

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
            ).lower()

        if choice_site in (2, 3):
            e6_incl_pending_alias = get_input(
                "(E621) Do you want to include 'pending' alias tags? (y/N)", DEFAULTS["e6_incl_pending_alias"]
            ).lower()
            e6_incl_deleted_alias = get_input(
                "(E621) Do you want to include alias tags that aren't in use by e621 anymore (deleted aliases)? (y/N)",
                DEFAULTS["e6_incl_deleted_alias"],
            ).lower()
    else:
        dbr_incl_deleted_alias = "n"
        e6_incl_pending_alias = "n"
        e6_incl_deleted_alias = "n"
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
    #         .lower()
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
        "choice_site": choice_site,
        "min_post_thresh": min_post_thresh,
        "incl_aliases": incl_aliases,
        "dbr_incl_deleted_alias": dbr_incl_deleted_alias,
        "e6_incl_pending_alias": e6_incl_pending_alias,
        "e6_incl_deleted_alias": e6_incl_deleted_alias,
        # "create_wildcard": create_wildcard,
        # "wildcard_categories": wildcard_categories,
    }
