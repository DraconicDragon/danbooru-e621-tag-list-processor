## todo file for new merge strategy/method

- [ ] Is input working
- [ ] Is new method working
  - [ ] new column called `services` with string as content, services separated by comma
  - [ ] what about post count, do i put it in another separate column or make the third column different type? like `tag,0,"danbooru:2349;e621:9867","alias1,alias2","danbooru,e621"`?
- [ ] add way of converting existing danbooru.csv and e621 csv to new method
- [ ] is this really necessary?
  - [ ] the optimal way would be that developers implement a way to load multiple csv files and sort by themselves instead of having a single file
    - [ ] but i agree that merged file is way more convenient, which is the same reason why they exist in the first place
  - [ ] I suspect i will come to the conclusion that this is unnecessary to implement.
