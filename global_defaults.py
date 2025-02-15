E621_BASE_URL = "https://e621.net/db_export/"  # come in csv format compressed in gz file

DBR_BASE_URL = "https://danbooru.donmai.us/tags.json?limit=1000&search[hide_empty]=yes&search[is_deprecated]=no&search[order]=count"  # 1000 is upper limit
DBR_ALIAS_URL = "https://danbooru.donmai.us/tag_aliases.json?commit=Search&limit=1000&search[order]=tag_count"  # 1000 is upper limit

DEFAULTS = {
    "choice_site": 3,
    "min_post_thresh": 2500,  # default to 30 instead 50 cuz noobai apparently knows all artists presumably but not really?, some arent trained as much but some are
    # problem: lower thresh = larger file, might cause performance issues with autocomplete speed (forge/a1111)? test needed
    # "included_categories": [0,1,2,3,4,5], # kinda useless for this program so is excluded;
    # 0: General, 1: Artist, 2: unkown?, 3: Copyright/series, 4: Character, 5: Meta DBR/ species e621, 6: disambiguation? e621, 7: Quality/Meta? e621?, 8: idk, lore e621?
    # todo: rework this comment
    "incl_aliases": "y",
    "dbr_incl_deleted_alias": "y",
    "e6_incl_pending_alias": "n",  # shouldn't be needed
    "e6_incl_deleted_alias": "y",
    "create_wildcard": 4,  # 1: DBR, 2: E6, 3: Both, 4: None
    "wildcard_categories": [1, 2, 3],  # 1: Artist, 2: Character, 3: Copyright/Series
    # "wildcard_sorting": 2,  # 1: Alphabetical, 2: Post count # not needed with yaml wildcard
}
