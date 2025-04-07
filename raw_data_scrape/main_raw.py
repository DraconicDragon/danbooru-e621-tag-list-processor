import asyncio
import json
import os
from datetime import datetime

import aiohttp

from defaults import DBR_SCRAPE_TARGETS

# todo: unified output folder


def create_output_directory(site: str) -> str:
    """
    Creates the output directory in ../raw/ with the current date (yearmonthdayhourminute)
    and returns the full path.
    """

    base_dir = os.path.dirname(os.path.abspath(__file__))
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
    output_dir = os.path.join(base_dir, "..", "output", "raw", site, date_str)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def get_base_filename(url: str) -> str:
    """
    Extracts the base filename (e.g. "tags.json") from the URL.
    """
    filename = url.rsplit("/", 1)[-1].split("?")[0]
    return filename


async def scrape_page(session, base_url: str, page: int):
    """
    Scrapes a single page by appending the page parameter to the URL.
    """
    if "?" in base_url:
        page_url = f"{base_url}&page={page}"
    else:
        page_url = f"{base_url}?page={page}"

    try:
        async with session.get(page_url) as response:
            response.raise_for_status()
            data = await response.json()
            return data
    except Exception as e:
        print(f"Error scraping page {page} from {base_url}: {e}")
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
    """

    async with aiohttp.ClientSession() as session:
        danbooru_output_dir = create_output_directory("danbooru")
        e621_output_dir = create_output_directory("e621")

        # Process Danbooru targets first.
        for target_id in settings.get("dbr_scrape_selection", []):
            target = DBR_SCRAPE_TARGETS.get(target_id)
            if target is None:
                print(f"Target ID {target_id} not found in DBR_SCRAPE_TARGETS.")
                continue
            await scrape_target(session, target, danbooru_output_dir)

        # Process additional targets (e.g., e621) if needed.
        for target_id in settings.get("e6_scrape_selection", []):
            print(f"Processing e6 target {target_id}... (Not implemented)")
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
