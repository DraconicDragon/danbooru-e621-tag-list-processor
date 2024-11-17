## Create and Format Danbooru and e621 Tags for AI Autocomplete Extensions
This script scrapes tags from Danbooru and downloads e621 tags from the DB export index, formatting them for AI autocomplete extensions. It can generate separate or merged tag lists for Danbooru and e621, with options like alias inclusion, minimum post thresholds, and filtering by alias status.

Output CSV files have been tested with [sd-webui-tagcomplete](https://github.com/DominikDoom/a1111-sd-webui-tagcomplete) and [pythongosssss/ComfyUI-Custom-Scripts](https://github.com/pythongosssss/ComfyUI-Custom-Scripts) autocomplete feature

### The lists I made are also available on CivitAI https://civitai.com/models/950325
The tag lists are automatically updated every 2 months by a GitHub actions workflow and saved in the tag-lists folder so even if I forget to update the tag lists manually, they will always be updated automatically.

## Running the Script Yourself
- Install the dependencies first `pip install pandas requests beautifulsoup4` or from the txt files `pip install -r requirements.txt` <sub>personal note: future pandas version do not handle NaNs on concat iirc so might need to update code</sub>
- Run the script and answer the questions after which the processing begins.
- You can also just spam enter to use the default values which will give you both Danbooru and e621 tag lists including active and deleted aliases and the merged list.

The tag lists should be saves in the same directory as the script when it's done (to check you can just check the output, it should print out the location of the saved files.)

Danbooru scraping part in the code was copied from here (many thank): https://github.com/BetaDoggo/danbooru-tag-list

im bad at repo titles

<sub>personal note2 because im too lazy to do something about it: regarding pandas dbr_e6_tag_processor.py:175: FutureWarning: The behavior of DataFrame concatenation with empty or all-NA entries is deprecated. In a future version, this will no longer exclude empty or all-NA columns when determining the result dtypes. To retain the old behavior, exclude the relevant entries before the concat operation.
  tag_df = pd.concat([tag_df, pd.DataFrame(data)], ignore_index=True)</sub>
