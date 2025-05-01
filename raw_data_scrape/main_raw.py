import asyncio
import json
import os
from datetime import datetime, timezone

import aiohttp

from defaults import DBR_SCRAPE_TARGETS
from tag_lists.e621 import get_latest_e621_tags_file_url


def create_output_directory(date_str, site: str) -> str:
    """
    Creates the output directory in ../output/raw/ with the current date (year-month-day_hour-minute) as a subdirectory.
    The directory structure is: ../output/raw/<site>/<date>.
    """

    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "..", "output", "raw", site, date_str)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def get_base_filename(url: str) -> str:
    """
    Extracts the base filename (e.g. "tags.json") from the URL.
    """
    filename = url.rsplit("/", 1)[-1].split("?")[0]
    return filename


async def scrape_page(session, base_url, page, max_retries=5, backoff=3):
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
                resp.raise_for_status()
                data = await resp.json()
                if attempt > 1:
                    print(f"Successfully retried page {page} on attempt {attempt}.")
                return data
        except Exception as e:
            print(f"[Attempt {attempt}/{max_retries}] Error scraping page {page}: {e}")
            if attempt < max_retries:
                await asyncio.sleep(backoff * attempt)
            else:
                print(f"Giving up on page {page} after {max_retries} attempts.")
                return None


async def scrape_target(session, target: dict, output_dir: str):
    """
    Processes one scraping target (a URL) in batches of 5 pages concurrently.
    Merges all pages' JSON data in the order they were scraped.
    Saves the final merged JSON once no more content is found.
    """
    target_name = target["name"]
    url = target["url"]
    base_filename = get_base_filename(url)
    page = 0  # starting page index
    batch_size = 5
    merged_data = []  # To accumulate data from each page

    print(f"\nStarting scraping for target '{target_name}' ({url})")
    while True:
        # Launch a batch of tasks (each task is one page)
        tasks = [scrape_page(session, url, page + i) for i in range(batch_size)]
        results = await asyncio.gather(*tasks)
        pages_processed = list(range(page, page + batch_size))
        print(f"Target '{target_name}': Processed pages {pages_processed}")

        # Check if the entire batch returned no content
        # NOTE: This check assumes that if all results are None or empty, AT LEAST 5 requests will be made unnecessarily
        if all(
            result is None or (isinstance(result, list) and not result) or (isinstance(result, dict) and not result)
            for result in results
        ):
            print(f"Target '{target_name}': No more content found. Finishing scraping.")
            break

        # Append results in the order of pages processed
        for result in results:
            if result is not None and result:
                if isinstance(result, list):
                    merged_data.extend(result)
                else:
                    merged_data.append(result)
        page += batch_size

    # After finishing, save the merged data to one JSON file.
    output_file = os.path.join(output_dir, base_filename)
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        print(f"Target '{target_name}': Merged data saved to {output_file}")
    except Exception as e:
        print(f"Failed to save merged data for target '{target_name}': {e}")


async def main(settings: dict):
    """
    Main async function. Opens one aiohttp session and processes each target
    specified in settings sequentially. For each target, pages are scraped
    concurrently in batches of 5, and the JSON data is merged and saved.
    5 because 5 is a nice number. (actually is for ratelimits, initially)
    """

    # todo: check if ratelimits are hit and maybe slow down operation if needed

    date = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M")

    async with aiohttp.ClientSession() as session:

        # Process Danbooru targets first.
        for target_id in settings.get("dbr_scrape_selection", []):
            danbooru_output_dir = create_output_directory(
                date, "danbooru"
            )  # NOTE: maybe better possible, i forgot, too long ago
            target = DBR_SCRAPE_TARGETS.get(target_id)
            if target is None:
                print(f"Target ID {target_id} not found in DBR_SCRAPE_TARGETS.")
                continue
            await scrape_target(session, target, danbooru_output_dir)

        # Process additional targets (e.g., e621) if needed.
        # todo: unfinished
        for target_id in settings.get("e6_scrape_selection", []):
            e621_output_dir = create_output_directory(date, "e621")
            print(f"Processing e6 target {target_id}... (Not implemented)")
            url = get_latest_e621_tags_file_url("https://e621.net/db_export/", alias_requested=False)
            # target = E621_SCRAPE_TARGETS.get(target_id)
            # if target is None:
            #     print(f"Target ID {target_id} not found in E621_SCRAPE_TARGETS.")
            #     continue
            # await scrape_target(session, target, e621_output_dir)


def do_thing(settings: dict):
    """
    Entry point for the asynchronous scraping.
    The settings dict defines which targets to scrape.
    """
    asyncio.run(main(settings))
