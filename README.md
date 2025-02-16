## Create and Format Danbooru and e621 Tags for AI Autocomplete Extensions and Krita AI diffusion

This script scrapes tags from Danbooru and downloads e621 tags from the DB export index, formatting them for AI autocomplete extensions. It can generate separate or merged tag lists for Danbooru and e621, with options like alias inclusion, minimum post thresholds, and filtering by alias status.

The CivitAI page for these can be found here: <https://civitai.com/models/950325>
All CSV files can be found here: <https://github.com/DraconicDragon/dbr-e621-lists-archive>

Output CSV files have been tested with [sd-webui-tagcomplete](https://github.com/DominikDoom/a1111-sd-webui-tagcomplete) and [pythongosssss/ComfyUI-Custom-Scripts](https://github.com/pythongosssss/ComfyUI-Custom-Scripts) autocomplete feature

~~The tag lists are automatically updated every 2 months by a GitHub actions workflow and saved in the tag-lists folder so even if I forget to update the tag lists manually, they will always be updated automatically.~~ yeah lol thats not working

## Running the Script Yourself

#### Method 1: Local

- Install the dependencies first `pip install pandas requests beautifulsoup4` or from the txt file `pip install -r requirements.txt`
- Run `python3 main.py` and answer the questions after which the processing begins.
- You can also just spam enter to use the default values which will give you both Danbooru and e621 tag lists including active and deleted aliases and the merged list.

The tag lists should be saved in the same directory as the script when it's done (to check you can just check the terminal output, it should print out the location of the saved files)

#### Method 2 (Requires GitHub account): GitHub actions

- SOON:tm::tm:
- Fork this repo
- Go to the "Actions" tab of the forked repo
- Select the X on the left
- Click X on the right and the workflow with optional custom settings
- Wait for the workflow to finish and go to X and scroll down, you will be able to download the artifact there which should contain the output CSV file(s)

Danbooru scraping part in the code was copied from here (many thank): <https://github.com/BetaDoggo/danbooru-tag-list>

im bad at repo names

<sub>personal note regarding pandas because im too lazy to actually read it: dbr_e6_tag_processor.py:175: FutureWarning: The behavior of DataFrame concatenation with empty or all-NA entries is deprecated. In a future version, this will no longer exclude empty or all-NA columns when determining the result dtypes. To retain the old behavior, exclude the relevant entries before the concat operation.
  tag_df = pd.concat([tag_df, pd.DataFrame(data)], ignore_index=True)</sub>
