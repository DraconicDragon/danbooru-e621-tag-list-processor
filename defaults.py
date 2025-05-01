E621_BASE_URL = "https://e621.net/db_export/"  # come in csv format compressed in gz file

DBR_BASE_URL = "https://danbooru.donmai.us/tags.json?limit=1000&search[hide_empty]=yes&search[is_deprecated]=no&search[order]=count"  # 1000 is upper limit
DBR_ALIAS_URL = "https://danbooru.donmai.us/tag_aliases.json?commit=Search&limit=1000&search[order]=tag_count"  # 1000
DBR_IMPLICATIONS_URL = "https://danbooru.donmai.us/tag_implications.json?limit=1000&search[order]=tag_count"  # 1000
DBR_POSTS_URL = "https://danbooru.donmai.us/posts.json?limit=200"  # 200 is upper limit
DBR_ARTISTS_URL = "https://danbooru.donmai.us/artists.json?limit=1000&search[order]=post_count"  # 1000 is upper limit
DBR_POOLS_URL = "https://danbooru.donmai.us/pools.json?limit=1000&search[order]=post_count"  # 1000 is upper limit
DBR_COMMENTS_URL = "https://danbooru.donmai.us/comments.json?limit=1000&search[order]=post_id"  # 1000 is upper limit
DBR_NOTES_URL = "https://danbooru.donmai.us/notes.json?limit=1000&search[order]=post_id"  # 1000 is upper limit
DBR_WIKI_PAGES_URL = "https://danbooru.donmai.us/wiki_pages.json?limit=1000&search[order]=title"  # 1000 is upper limit
DBR_USERS_URL = "https://danbooru.donmai.us/users.json?limit=1000&search[order]=name"  # 1000 is upper limit

DBR_SCRAPE_TARGETS = {
    1: {
        "name": "Tags",
        "url": DBR_BASE_URL,
        "note": "(🟢|Suggested; The normal mode can use this to create tag lists from (Not Implemented))",
        "suggested": True,
    },
    2: {
        "name": "Aliases",
        "url": DBR_ALIAS_URL,
        "note": "(🟢|Suggested; The normal mode can use this to create tag lists from (Not Implemented))",
        "suggested": True,
    },
    3: {
        "name": "Implications",
        "url": DBR_IMPLICATIONS_URL,
        "note": "",
        "suggested": True,
    },
    4: {
        "name": "Posts",
        "url": DBR_POSTS_URL,
        "note": "(⚠️|Many/Takes long AND can't go beyond page 1000 (does NOT contain any image files, only URL); please see actual dumps for full data, possibly deepghs' dataset on Huggingface has it)",
        "suggested": True,
    },
    5: {
        "name": "Artists",
        "url": DBR_ARTISTS_URL,
        "note": "",
        "suggested": False,
    },
    6: {
        "name": "Pools",
        "url": DBR_POOLS_URL,
        "note": "",
        "suggested": False,
    },
    7: {
        "name": "Comments",
        "url": DBR_COMMENTS_URL,
        "note": "(⚠️|More than 1000 pages)",
        "suggested": False,
    },
    8: {
        "name": "Notes",
        "url": DBR_NOTES_URL,
        "note": "(⚠️|More than 1000 pages)",
        "suggested": False,
    },
    9: {
        "name": "Wiki Pages",
        "url": DBR_WIKI_PAGES_URL,
        "note": "(API response is in an undesirable format/Not much use in that format)",
        "suggested": False,
    },
    10: {
        "name": "Users",
        "url": DBR_USERS_URL,
        "note": "(⚠️|lots of internal server errors for some reason, stops at page 150 too?)",
        "suggested": False,
    },
}

E6_SCRAPE_TARGETS = {
    1: {
        "name": "Tags",
        "note": "(🟢|Suggested)",
        "suggested": True,
    },
    2: {
        "name": "Aliases",
        "note": "(🟢|Suggested)",
        "suggested": True,
    },
    3: {
        "name": "Implications",
        "note": "",
        "suggested": True,
    },
    4: {
        "name": "Posts",
        "note": "(⚠️|Many/Takes very long | 1.4gb as of 6th April 2025)",
        "suggested": True,
    },
    5: {
        "name": "Pools",
        "note": "",
        "suggested": False,
    },
    6: {
        "name": "Wiki Pages",
        "note": "(API response is in an undesirable format/Not much use in that format)",
        "suggested": False,
    },
}


DEFAULTS = {
    "choice_site": 3,
    "merged_post_count_type": 3,  # 1: Danbooru, 2: e621, 3: Sum of Both
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
