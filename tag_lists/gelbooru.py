# tag_lists/gelbooru.py

import asyncio
import html
import json
import os
from datetime import datetime

import aiohttp
import pandas as pd

from defaults import GELBOORU_BASE_URL

# Path setup
current_directory = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_directory)
output_dir = os.path.join(project_root, "output")
raw_data_dir = os.path.join(output_dir, "raw_data")

# Checkpoint file paths
CHECKPOINT_FILE = os.path.join(raw_data_dir, "gelbooru_checkpoint.json")
PARTIAL_DATA_FILE = os.path.join(raw_data_dir, "gelbooru_partial.jsonl")


def normalize_tag_text(value):
    if isinstance(value, str):
        return html.unescape(value)
    return value


def save_checkpoint(pid):
    """Saves the current progress safely."""
    temp_checkpoint = CHECKPOINT_FILE + ".tmp"
    with open(temp_checkpoint, "w") as f:
        json.dump({"last_pid": pid, "timestamp": str(datetime.now())}, f)
    os.replace(temp_checkpoint, CHECKPOINT_FILE)  # Atomic swap


def load_checkpoint():
    """Returns the last saved PID if it exists."""
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r") as f:
                return json.load(f).get("last_pid", 0)
        except Exception as e:
            print(f"Error loading checkpoint: {e}")
            return 0
    return 0


def append_partial_data(tags):
    """Appends tags to a JSONL file (one JSON object per line)."""
    with open(PARTIAL_DATA_FILE, "a", encoding="utf-8") as f:
        for tag in tags:
            if isinstance(tag, dict) and "name" in tag:
                tag["name"] = normalize_tag_text(tag["name"])
            f.write(json.dumps(tag, ensure_ascii=False) + "\n")


def finalize_raw_data():
    """Merges partial JSONL into a single final JSON for HuggingFace."""
    if not os.path.exists(PARTIAL_DATA_FILE):
        return []

    print("\nFinalizing raw data into HF-ready JSON...")
    all_tags = []
    with open(PARTIAL_DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                tag = json.loads(line)
                if isinstance(tag, dict) and "name" in tag:
                    tag["name"] = normalize_tag_text(tag["name"])
                all_tags.append(tag)

    date_str = datetime.now().strftime("%Y-%m-%d")
    final_path = os.path.join(raw_data_dir, f"gelbooru_tags_raw_{date_str}.json")

    with open(final_path, "w", encoding="utf-8") as f:
        json.dump(all_tags, f, ensure_ascii=False, indent=2)

    print(f"Final JSON saved: {final_path}")

    return all_tags


async def scrape_batch(session, base_url, pid, api_key, user_id):
    params = {
        "page": "dapi",
        "s": "tag",
        "q": "index",
        "json": "1",
        "limit": "100",
        "pid": str(pid),
    }
    if api_key and user_id:
        params["api_key"], params["user_id"] = api_key, user_id

    for attempt in range(1, 6):
        try:
            async with session.get(base_url, params=params, timeout=15) as resp:
                if resp.status == 429:
                    await asyncio.sleep(10 * attempt)
                    continue
                resp.raise_for_status()
                data = await resp.json()
                return data, resp.status
        except Exception as e:
            print(f"Error scraping PID {pid}: {e}")
            await asyncio.sleep(2 * attempt)
    return None, None


async def scrape_target(session, url):
    api_key = os.getenv("GELBOORU_API_KEY", "")
    user_id = os.getenv("GELBOORU_USER_ID", "")
    os.makedirs(raw_data_dir, exist_ok=True)

    current_pid = load_checkpoint()
    if current_pid > 0:
        print(f"\n>>> Resuming Gelbooru scrape from PID: {current_pid}")

    batch_size = 5
    estimated_total_pids = 19500

    while True:
        tasks = [scrape_batch(session, url, current_pid + i, api_key, user_id) for i in range(batch_size)]
        raw_results = await asyncio.gather(*tasks)

        batch_tags = []
        finished = False

        for result, status in raw_results:
            page_tags = (
                result.get("tag", []) if isinstance(result, dict) else (result if isinstance(result, list) else [])
            )
            if not page_tags:
                finished = True
            else:
                for tag in page_tags:
                    if isinstance(tag, dict) and "name" in tag:
                        tag["name"] = normalize_tag_text(tag["name"])
                batch_tags.extend(page_tags)

        if batch_tags:
            append_partial_data(batch_tags)
            current_pid += batch_size
            save_checkpoint(current_pid)

        progress = min(100, (current_pid / estimated_total_pids) * 100)
        print(f"Gelbooru: {progress:.2f}% | Pid: {current_pid} | Checkpointed", end="\r")

        if finished:
            print(f"\nGelbooru: End of data reached at PID {current_pid}")
            break

        await asyncio.sleep(0.05)

    return finalize_raw_data()


async def process_gb_tags_async(settings):
    async with aiohttp.ClientSession() as session:
        raw_json = await scrape_target(session, GELBOORU_BASE_URL)
        if not raw_json:
            return pd.DataFrame()

        df = pd.DataFrame(raw_json)
        if df.empty:
            return pd.DataFrame()

        if "name" in df.columns:
            df["name"] = df["name"].astype(str).map(normalize_tag_text)

        # Clean & Filter for Autocomplete CSV
        df["count"] = pd.to_numeric(df["count"], errors="coerce").fillna(0).astype(int)
        df["type"] = pd.to_numeric(df["type"], errors="coerce").fillna(0).astype(int)

        df = df[(df["count"] >= int(settings["min_post_thresh"])) & (df["type"] != 6)]

        df = df.rename(columns={"count": "post_count", "type": "category"})
        df = df[["name", "category", "post_count"]].sort_values(by="post_count", ascending=False)
        df["aliases"] = ""
        return df


def process_gb_tags(settings):
    return asyncio.run(process_gb_tags_async(settings))
