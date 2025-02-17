E621_BASE_URL = "https://e621.net/db_export/"  # come in csv format compressed in gz file

DBR_BASE_URL = "https://danbooru.donmai.us/tags.json?limit=1000&search[hide_empty]=yes&search[is_deprecated]=no&search[order]=count"  # 1000 is upper limit
DBR_ALIAS_URL = "https://danbooru.donmai.us/tag_aliases.json?commit=Search&limit=1000&search[order]=tag_count"  # 1000 is upper limit

DEFAULTS = {
    "choice_site": 3,
    "min_post_thresh": 25,  # default to 25 cause noobai can represent tags with sometimes even 20 tags. 25 is a good default i think
    # problem: lower thresh = larger file, might cause performance issues with autocomplete speed (forge/a1111)? test needed
    # check the table for category index meaning here: https://github.com/DraconicDragon/dbr-e621-lists-archive/tree/main/tag-lists/danbooru_e621_merged
    "incl_aliases": "y",
    "dbr_incl_deleted_alias": "y",
    "e6_incl_pending_alias": "n",  # shouldn't be needed usually
    "e6_incl_deleted_alias": "y",
    "create_krita_csv": "n",  # creates krita compatible autocomplete csvs
    "create_wildcard": 4,  # 1: DBR, 2: E6, 3: Both, 4: None
    # NOTE: wildcard stuff not in use currently, will probably be separate stuff
    "wildcard_categories": [1, 2, 3],  # 1: Artist, 2: Character, 3: Copyright/Series
    # "wildcard_sorting": 2,  # 1: Alphabetical, 2: Post count # not needed with yaml wildcard
}
