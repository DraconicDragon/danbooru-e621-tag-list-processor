import asyncio

import aiohttp
import pandas as pd

from defaults import DBR_SCRAPE_TARGETS
from modules.merge_utils import add_aliases


def convert_json_to_df(json_data):
    return pd.DataFrame(json_data)


def stop_if_below_post_threshold(item, settings):
    if "post_count" in item:
        return int(item["post_count"]) < int(settings["min_post_thresh"])
    return False


async def process_dbr_tags_async(settings):
    async with aiohttp.ClientSession() as session:
        df1_target = DBR_SCRAPE_TARGETS.get(1)  # 1 = Tags, 2 = Aliases
        df1_json = await scrape_target(
            session,
            df1_target["url"],
            df1_target["name"],
            stop_check=stop_if_below_post_threshold,
            settings=settings,
        )
        df1 = convert_json_to_df(df1_json)
        df1 = df1[df1["post_count"] >= settings["min_post_thresh"]]
        df1 = df1[["name", "category", "post_count"]]
        df1 = df1.sort_values(by="post_count", ascending=False)

        if settings.get("incl_aliases") == "y":
            df2_target = DBR_SCRAPE_TARGETS.get(2)  # 1 = Tags, 2 = Aliases
            df2_json = await scrape_target(
                session,
                df2_target["url"],
                df2_target["name"],
                stop_check=stop_if_below_post_threshold,
                settings=settings,
            )
            df2 = convert_json_to_df(df2_json)
            if settings.get("dbr_incl_deleted_alias") == "n":
                df2 = df2[df2["status"] == "active"]
            df2 = df2[["antecedent_name", "consequent_name"]]
            return add_aliases(df1, df2)
        else:
            df1["aliases"] = ""
            return df1


async def scrape_page(session, base_url, page, max_retries=3, backoff=3):
    """
    Scrapes a single page by appending the page parameter to the URL.
    """
    if "?" in base_url:
        page_url = f"{base_url}&page={page}"
    else:
        page_url = f"{base_url}?page={page}"

    for attempt in range(1, max_retries + 1):
        try:
            async with session.get(page_url) as resp:
                if resp.status == 410:
                    print(f"Page {page} returned 410 Gone — skipping retries.")
                    return "GONE", 410
                resp.raise_for_status()
                data = await resp.json()
                if attempt > 1:
                    print(f"Successfully retried page {page} on attempt {attempt}.")
                return data, resp.status
        except aiohttp.ClientResponseError as e:
            if e.status == 410:
                print(f"Page {page} returned 410 Gone — skipping retries.")
                return "GONE", 410
            print(f"[Attempt {attempt}/{max_retries}] Error scraping page {page}: {e}")
            last_status = e.status
        except Exception as e:
            print(f"[Attempt {attempt}/{max_retries}] Error scraping page {page}: {e}")
            last_status = None

        if attempt < max_retries:
            await asyncio.sleep(backoff * attempt)

    print(f"Giving up on page {page} after {max_retries} attempts.")
    return None, last_status


async def scrape_target(session, url, target_name, stop_check=None, settings=None):
    """
    Processes one scraping target (a URL) in batches of 5 pages concurrently.
    Merges all pages' JSON data in the order they were scraped.
    Saves the final merged JSON once no more content is found.
    """
    page = 1  # starting page
    batch_size = 5
    merged_data = []  # To accumulate data from each page

    print(f"\nStarting scraping for target '{target_name}' ({url})")
    while True:
        # Launch a batch of tasks (each task is one page)
        tasks = [scrape_page(session, url, page + i) for i in range(batch_size)]
        raw_results = await asyncio.gather(*tasks)
        results = []
        pages_with_status = []

        for i, (result, status) in enumerate(raw_results):
            page_num = page + i
            results.append(result)
            if status and status != 200:
                pages_with_status.append(f"{page_num}({status})")
            else:
                pages_with_status.append(f"{page_num}")

        print(f"Target '{target_name}': Processed pages [{', '.join(pages_with_status)}]")

        # Check if the entire batch returned no content
        # NOTE: This check assumes that if all results are None or empty, AT LEAST 5 requests will be made unnecessarily
        if all(
            result in [None, "GONE"]
            or (isinstance(result, list) and not result)
            or (isinstance(result, dict) and not result)
            for result in results
        ):
            print(f"Target '{target_name}': No more content found. Finishing scraping.")
            break

        # Append results in the order of pages processed
        for result, _ in raw_results:
            if result is not None and result != "GONE":
                if isinstance(result, list):
                    merged_data.extend(result)
                else:
                    merged_data.append(result)

        if stop_check:
            for item in merged_data[-batch_size:]:
                if stop_check(item, settings):
                    print(
                        f"Target '{target_name}': Early stop."
                        f"'{item.get('name', 'N/A')}' post_count={item.get('post_count', 'N/A')} < threshold {settings.get('min_post_thresh', '?')}"
                    )
                    return merged_data

        page += batch_size

    return merged_data


def process_dbr_tags(settings):
    """
    Process Danbooru tags and aliases asynchronously.
    """
    return asyncio.run(process_dbr_tags_async(settings))
