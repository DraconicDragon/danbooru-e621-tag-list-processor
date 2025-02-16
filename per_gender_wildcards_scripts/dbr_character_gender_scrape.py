import asyncio
import os
import re

import aiohttp
import pandas as pd

# NOTE: THIS IS THE FIRST PASS; ITLL TAKE VERY LONG TO PROCESS ALL TAGS
# suggestion is to stop at 25 or even higher, the lower you go the more indeterminate charas there are

script_dir = os.path.dirname(os.path.abspath(__file__))

input_file = os.path.join(script_dir, "danbooru_tags_2024-12-22_pt2-ia-dd-ed.csv")
female_file = os.path.join(script_dir, "female_tags.txt")
male_file = os.path.join(script_dir, "male_tags.txt")
indeterminate_file = os.path.join(script_dir, "indeterminate_tags.txt")

df = pd.read_csv(input_file)

# filter rows where second column equals 4 (character tag)
filtered_df = df[df.iloc[:, 1] == 4]

female_tags = []
male_tags = []
indeterminate_tags = []


async def get_character_gender(session, tag: str) -> dict:
    counter = 0
    base_url = "https://danbooru.donmai.us/posts.json"
    params = {
        "tags": f"{tag}",  # search ordered by oldest post of specified tag | order by id
        "limit": 200,  # X posts per page, limit for standard user is 200 i think
        "page": 0,  # start first page
    }

    try:
        while True:  # loop through pages until valid post is found or error
            async with session.get(base_url, params=params) as response:
                response.raise_for_status()  # successful response insurance TM
                posts = await response.json()

                if not posts:
                    return {
                        "id": -1,
                        "file_url": "N/A",
                        "tags": "N/A",
                        "gender": "Indeterminate",
                    }

                for post in posts:
                    # extract tags from the post
                    tags = post["tag_string"].split()
                    character_tags = post.get("tag_string_character", "").split()
                    gen_tags = post.get("tag_string_general", "").split()

                    # region filter conditions
                    # conditions to skip posts, ignore posts with this
                    if len(character_tags) > 1:  # more than one character in the post
                        continue
                    if not "solo" in gen_tags:  # if both 1boy and 1girl
                        continue

                    if "genderswap" in gen_tags:  # genderswap tag, needs testing
                        continue
                    if any(
                        tag in gen_tags
                        for tag in ["multiple_girls", "multiple_boys", "2girls", "2boys", "2others", "multiple_views"]
                    ):
                        continue
                    if not (
                        "1boy" in gen_tags or "1girl" in gen_tags or "1other" in gen_tags
                    ):  # neither 1boy nor 1girl
                        continue
                    if any(  # testing, monster related
                        tag in gen_tags
                        for tag in [
                            "animalization",
                            "foodification",
                            "furrification",
                            "humanization",
                            "mechanization",
                            "monsterification",
                            "objectification",
                            "personification",
                            "vehicalization",
                        ]
                    ):
                        continue
                    # endregion

                    # valid post found
                    if "1boy" in gen_tags:
                        gender = "Male"
                    elif "1girl" in gen_tags:
                        gender = "Female"
                    elif "1other" in gen_tags:
                        gender = "Indeterminate"

                    return {
                        "id": post["id"],
                        "file_url": post.get("file_url", "N/A"),
                        "tags": tags,
                        "gender": gender,
                    }

                counter += 1

                # alternates between newest and oldest posts
                # NOTE: technically not needed, doesnt impact speed anyway
                if counter % 2 == 0:
                    params["tags"] = f"{tag} order:id"
                else:
                    params["page"] += 1
                    params["tags"] = f"{tag}"

                print(f"Tag: \033[33m{tag}\033[0m | Page: " + str(counter) + "...", end="\r")

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


async def process_batch(session, tags_batch):
    tasks = [get_character_gender(session, tag) for tag in tags_batch]
    results = await asyncio.gather(*tasks)

    for tag, post in zip(tags_batch, results):
        print(f"Processing tag: \033[33m{tag}\033[0m...")

        processed_tag = re.sub(r"([\(\)])", r"\\\1", tag).replace("_", " ")

        if post and post["gender"] == "Female":
            print(f"Determined gender for tag {tag}: \033[31m{post['gender']}\033[0m")
            with open(female_file, "a") as f:
                f.write(f"{processed_tag}\n")

        elif post and post["gender"] == "Male":
            print(f"Determined gender for tag {tag}: \033[34m{post['gender']}\033[0m")
            with open(male_file, "a") as f:
                f.write(f"{processed_tag}\n")

        elif post and post["gender"] == "Indeterminate":
            print(f"Determined gender for tag {tag}: \033[32mindeterminate\033[0m")
            with open(indeterminate_file, "a") as f:
                f.write(f"{processed_tag}\n")

        else:
            print(f"\n\nweewoo {tag}'s gender couldn't be determined wee woo wee this line should never print!\n\n")


# NOTE: processes 5 tags at the same time but for each tag the pages scraped are still synchronous 1 at a time
async def main():
    tags = filtered_df.iloc[:, 0].tolist()  # Extract the tags as a list
    batch_size = 5  # NOTE: higher than 5 will result in 403

    # Read existing tags from files and normalize them
    existing_tags = set()
    for file_path in [female_file, male_file, indeterminate_file]:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                existing_tags.update(re.sub(r"\\", "", line.strip().replace(" ", "_")) for line in f)

    # Filter out tags that already exist in the files
    tags_to_process = [tag for tag in tags if tag not in existing_tags]

    async with aiohttp.ClientSession() as session:
        for i in range(0, len(tags_to_process), batch_size):
            batch = tags_to_process[i : i + batch_size]
            await process_batch(session, batch)


# start
asyncio.run(main())

print(f"Tags saved to files:\n- Female: {female_file}\n- Male: {male_file}\n- Indeterminate: {indeterminate_file}")
