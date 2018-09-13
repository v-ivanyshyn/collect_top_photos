**This python script does the following stuff:**
- finds photos in source folder and reads their metadata (xmp, xattr, exif)
- checks if each photo has high rating (actually five stars)
- else checks if the photo has still good rating (four stars) and appropriate keywords ('I' or 'Me' meaning me is on the photo)
- if so, smarty copies the photo to target folder

**Why this is needed at all?**
In my case I have a lot of good photos on a Mac, properly rated and tagged with keywords, and I want to have the best of them on an iPhone. Sad but iOS Photos app is pretty poor for collections (the best feature it has - scrolling through thousands of all your photos to find that picture captured probably year or two ago...). So, with this script I pick five-star photos from my entire collection and copy them to iPhone via AirDrop.

**How to use it:**
- before running it with Python 2.7, check if all libraries from import section are present
- pass source folder with photos as first argument, target folder as second one
- run it and watch console output
- the script copies appropriate photos to target folder, renames them to include their date in filename and downscales
- next you may manually export these photos to your mobile device

You can safely run the script multiple times on the same source photos - it checks if each photo exists in target folder and if the metadata matches, if so it skips the photo.
