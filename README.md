## Scrapes tags from Danbooru and downloads e621 tags from db_export index and then formats them for use in AI related autocomplete extensions
This script let's you create an up to date tag list of either or both Danbooru and e621 with a few options like including aliases/aliases with a specific status only, minimum post threshold for a tag to be kept and either making a Danbooru or e621 only list, or both and merged.

This was made in mind with usage for:
- https://github.com/DominikDoom/a1111-sd-webui-tagcomplete
- https://github.com/pythongosssss/ComfyUI-Custom-Scripts Autocomplete feature


### The lists I made are also available on CivitAI https://civitai.com/models/950325

## Running the Script Yourself
- Install the dependencies first `pip install pandas requests beautifulsoup4`
- Run the script and answer the questions after which the processing begins.
- You can also just spam enter to use the default values which will give you both Danbooru and e621 tag lists including active and deleted aliases and the merged list.

The tag lists should be saves in the same directory as the script when it's done (to check you can just check the output, it should print out the location of the saved files.)

Danbooru scraping part in the code was copied from here (many thank): https://github.com/BetaDoggo/danbooru-tag-list
