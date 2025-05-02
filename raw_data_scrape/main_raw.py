import asyncio
import json
import os
import re
from datetime import datetime, timezone

import aiohttp
import requests

from defaults import DBR_SCRAPE_TARGETS, E6_SCRAPE_TARGETS, E621_BASE_URL
from modules.danbooru_scrape import scrape_target
from modules.e621_scrape import get_latest_e621_tags_file_info


def create_output_directory(date_str, site: str, override_time: str = None) -> str:
    """
    Creates the output directory in ../output/raw/ with the current date (year-month-day_hour-minute) as a subdirectory.
    If override_time is given, it replaces the time part (HH-MM) of the date_str.
    """
    if override_time:
        # Replace only the time portion
        date_str = re.sub(r"(_\d{2}-\d{2})$", f"_{override_time}", date_str)

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


def save_json(data, url, target_name, output_dir):
    # After finishing, save the merged data to one JSON file.
    base_filename = get_base_filename(url)
    output_file = os.path.join(output_dir, base_filename)
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
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

    date = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M")

    async with aiohttp.ClientSession() as session:

        # Process Danbooru targets first.
        for target_id in settings.get("dbr_scrape_selection", []):
            target = DBR_SCRAPE_TARGETS.get(target_id)
            if target is None:
                print(f"Target ID {target_id} not found in DBR_SCRAPE_TARGETS.")
                continue

            danbooru_output_dir = create_output_directory(date, "danbooru")

            url = target["url"]
            target_name = target["name"]
            data = await scrape_target(session, url, target_name)
            save_json(data, url, target_name, danbooru_output_dir)

        # Process e621 targets
        for target_id in settings.get("e6_scrape_selection", []):
            target = E6_SCRAPE_TARGETS.get(target_id)
            if target is None:
                print(f"Target ID {target_id} not found in E621_SCRAPE_TARGETS.")
                continue

            e621_latest_file_info = get_latest_e621_tags_file_info(E621_BASE_URL, target=target["name"].lower())
            url = e621_latest_file_info["url"]
            e621_output_dir = create_output_directory(date, "e621", override_time=e621_latest_file_info["time"])

            try:
                print(f"Downloading {target['name']} from {url}...")
                response = requests.get(url)
                response.raise_for_status()  # successful response insurance TM
            except requests.exceptions.RequestException as e:
                print(f"Failed to download data for target '{target['name']}': {e}")
                continue  # Skip to the next target if this one fails

            target_name = target["name"]
            base_filename = get_base_filename(url)
            output_file = os.path.join(e621_output_dir, base_filename)

            try:
                with open(output_file, "wb") as f:  # Open in binary write mode
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Target '{target_name}': Data saved to {output_file}")
            except Exception as e:
                print(f"Failed to save data for target '{target_name}': {e}")


def do_thing(settings: dict):
    """
    Entry point for the asynchronous scraping.
    The settings dict defines which targets to scrape.
    """
    asyncio.run(main(settings))
