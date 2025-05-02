i should've just read <https://github.com/Acly/krita-ai-diffusion/tree/main/ai_diffusion/tags> lol
i thought the bigquery was inaccessible by plebs turns out, im just dumb, just had to link it to my own project aaaaaaaaa
if i can make code so that user doesnt need to make their own bigquery project/google account then maybe therell be a bigquery branch
otherwise itll probably just make the raw data scrape mode of this project redundant

## Create Danbooru and e621 Tag Lists for AI related Autocomplete Extensions

This script scrapes tags from the Danbooru API and downloads e621 tags from <https://e621.net/db_export/> and formatting them for AI autocomplete extensions. It can create separate and merged tag lists for Danbooru and e621, with options like alias inclusion, minimum post thresholds, and filtering by alias status as well as creating [Krita AI diffusion](https://github.com/Acly/krita-ai-diffusion) compatible tag lists (unfiltered/NSFW versions only).

The CivitAI page for these can be found here: <https://civitai.com/models/950325>
An archive of CSV files I made can be found here: <https://github.com/DraconicDragon/dbr-e621-lists-archive>

### Links for programs and their autocomplete extensions

The named programs and their extensions below are only the ones I have tested and used myself. The default tag lists will likely work with other autocomplete programs/extensions.

- [A1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui)/[Forge](https://github.com/lllyasviel/stable-diffusion-webui-forge)/[reForge](https://github.com/Panchovix/stable-diffusion-webui-reForge):
  - Extension: [DominikDoom/a1111-sd-webui-tagcomplete](https://github.com/DominikDoom/a1111-sd-webui-tagcomplete)
  - Location of the tag lists should be in `/webui/extensions/a1111-sd-webui-tagcomplete/tags/`
  - To select the file you want to use go to your WebUI's settings tab, search for "tag filename" or look for "Tag Autocomplete" in the left sidebar and click that to get the tagcomplete settings and then select the tag file from the "Tag filename" drop-down.

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI):
  - Custom Node 1: [pythongosssss/ComfyUI-Custom-Scripts](https://github.com/pythongosssss/ComfyUI-Custom-Scripts)
    - ComfyUI Settings -> pysssss -> Manage custom words
      - I recommend pasting the CSV file content in the big textbox and saving it or using a link like [this one](https://raw.githubusercontent.com/DraconicDragon/dbr-e621-lists-archive/refs/heads/main/tag-lists/danbooru_e621_merged/danbooru_e621_merged_2024-12-22_pt25-ia-dd-ed_spc.csv) and load it. (gotten from [here](https://github.com/DraconicDragon/dbr-e621-lists-archive/blob/main/tag-lists/danbooru_e621_merged/danbooru_e621_merged_2024-12-22_pt25-ia-dd-ed_spc.csv) by pressing "Raw" button at top right)
      - When you press save it might take a short bit and the "Saved!" appears only for less than a second. I'm unsure if you need to wait for it to show to be able to dismiss the window/popup.

  - Custom Node 2: [jupo-ai/comfy-ex-tagcomplete](https://github.com/jupo-ai/comfy-ex-tagcomplete)
    - Seems like this extension already comes with tag lists that seems to be from the a1111-sd-tagcomplete extension, so you might not need to add any custom ones.
    - To add custom CSV files: Drop the CSV file you want to use in the `ComfyUI\custom_nodes\comfy-ex-tagcomplete\tags`
      - Refresh the ComfyUI tab if one is open, and then check ComfyUI Settings -> jupo -> tags file

- [SwarmUI](https://github.com/LykosAI/StabilityMatrix):
  - Please see: [Autocompletions.md#word-lists](https://github.com/mcmonkeyprojects/SwarmUI/blob/master/docs/Features/Autocompletions.md#word-lists)

- [Stability Matrix](https://github.com/LykosAI/StabilityMatrix): Settings -> Inference -> Auto Completion

- [Krita AI diffusion](https://github.com/Acly/krita-ai-diffusion):
  - Go to Settings -> Interface -> Tag Auto-Completion
    - You will see a refresh and folder icon on the right side. Click the folder icon and it should take you to the tags folder where you have to replace the tag files with the ones you want to use.
    <sub>Note: For me personally on Windows, the tags folder was in `%appdata%\krita\pykrita\ai_diffusion\tags` while the folder icon took me to `%appdata%\krita\ai_diffusion\tags` </sub>

- [SwarmUI](https://github.com/mcmonkeyprojects/SwarmUI)
  - Please see here: <https://github.com/mcmonkeyprojects/SwarmUI/blob/master/docs/Features/Autocompletions.md#word-lists>

~~The tag lists are automatically updated every 2 months by a GitHub actions workflow and saved in the tag-lists folder so even if I forget to update the tag lists manually, they will always be updated automatically.~~ yeah lol thats not working - will update at some point

## Running the Script Yourself

**INFO**: Hi, if you are looking to run this script yourself, i'd appreciate if you could look over the finished danbooru CSV (or JSON data if you use raw mode) and see if it's correct. I've recently changed the csv creation code to use the scraping code from raw mode but haven't really done thorough tests with it. If you don't want to have any potential issues even though i don't think there should be any, the latest commit id before this change is `f53900da102150e08feae8ba552d170f8540e6dd`

### Method 1: Local

- Install the dependencies first `pip install pandas requests beautifulsoup4 aiohttp` or from the txt file `pip install -r requirements.txt`
- Run `python3 main.py` and fill out the options - after this the processing begins
- You can also just spam enter to use the default values which will give you both Danbooru and e621 tag lists including active and deleted aliases and the merged list.

The tag lists should be saved in a folder called /output/tag_lists that will be created after the program successfully creates the CSV files (to check you can just check the terminal output, it should print out the location of the saved files)

### Method 2 (Requires GitHub account): GitHub actions

- SOON:tm::tm:
- Fork this repo
- Go to the "Actions" tab of the forked repo
- Select the X on the left
- Click X on the right and the workflow with optional custom settings
- Wait for the workflow to finish and go to X and scroll down, you will be able to download the artifact there which should contain the output CSV file(s)

#### Raw mode

There is a "Raw mode" which will allow you to scrape the raw data without turning it into tag lists. Simply enter "raw" for the first question/selection and follow the instructions.

Danbooru scraping part in the code was originally copied from here (many thank): <https://github.com/BetaDoggo/danbooru-tag-list>

im bad at repo names

<sub>personal note regarding pandas because im too lazy to actually read it: dbr_e6_tag_processor.py:175: FutureWarning: The behavior of DataFrame concatenation with empty or all-NA entries is deprecated. In a future version, this will no longer exclude empty or all-NA columns when determining the result dtypes. To retain the old behavior, exclude the relevant entries before the concat operation.
  tag_df = pd.concat([tag_df, pd.DataFrame(data)], ignore_index=True)</sub>
