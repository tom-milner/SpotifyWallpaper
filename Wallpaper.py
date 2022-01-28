from PIL import Image, ImageDraw, ImageFont
import functools
import os
import shutil
import sys
import random
import math
import spotipy
from spotipy.oauth2 import SpotifyPKCE
import json
import pprint
import requests
import screeninfo
from multiprocessing.pool import ThreadPool


def create_collage(covers, cols=3, rows=3):
    '''Create a collage from the provided list of album covers.'''
    w, h = Image.open(covers[0]).size
    collageWidth = cols * w
    collageHeight = rows * h
    new_image = Image.new('RGB', (collageWidth, collageHeight))
    cursor = (0, 0)
    for cover in covers:
        # place image
        new_image.paste(Image.open(cover), cursor)

        # move cursor
        y = cursor[1]
        x = cursor[0] + w
        if cursor[0] >= (collageWidth - w):
            y = cursor[1] + h
            x = 0
        cursor = (x, y)

    return new_image


def downloadAlbumCover(track):
    '''Download the album cover of a spotify track.'''
    album = track["album"]
    albumCoverLink = album["images"][0]["url"]

    print(f'Attempting to download: {album["name"]} ({albumCoverLink})')

    r = requests.get(albumCoverLink, stream=True)

    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True
        # Open a local file with wb ( write binary ) permission.
        filename = album["name"].replace("/", " ") + ".jpg"
        fullPath = albumCoverPath + "/" + filename
        with open(fullPath, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

        print('Image sucessfully downloaded: ', filename)
        return fullPath
    else:
        print('Image Couldn\'t be retrieved')


#  Get the duration to get the user's top tracks from.
validDurations = ["short_term", "medium_term", "long_term"]
if(len(sys.argv) < 2):
    print("No duration provided. Using default ({})".format(validDurations[0]))
    duration = validDurations[0]
else:
    duration = sys.argv[1]
    if duration not in validDurations:
        print("Invalid duration.")
        print("Valid durations are: {}".format(validDurations))
        exit(1)

# Download the user's top tracks.
scope = "user-top-read"
sp = spotipy.Spotify(auth_manager=SpotifyPKCE(scope=scope))
print("\nDownloading Top Tracks ({})...".format(duration))
topTracks = sp.current_user_top_tracks(limit=50, time_range=duration)["items"]

# Deduplicate multiple instances of same album.
print("Original Tracks: " + str(len(topTracks)))
dedupTrackAlbums = list(
    {track["album"]["name"]: track for track in topTracks}.values())
print("Deduped Albums: " + str(len(dedupTrackAlbums)))

#  Create the directory to store the album covers in.
albumCoverPath = "./AlbumCovers"
if os.path.exists(albumCoverPath):
    shutil.rmtree(albumCoverPath)
os.mkdir(albumCoverPath)

# Download the album covers using multiple threads to speed things up.
print("\nDownloading album covers...")
numThreads = 50
albumCoverPaths = list(ThreadPool(numThreads).imap_unordered(
    downloadAlbumCover, dedupTrackAlbums))
numCovers = len(albumCoverPaths)

# Create the directory to store the created wallpapers in.
wallpaperPath = "./SpotifyWallpapers"
if os.path.exists(wallpaperPath):
    shutil.rmtree(wallpaperPath)
os.mkdir(wallpaperPath)

print("\nCreating album covers:")

# Create a wallpaper for each of the user's monitors.
monitors = screeninfo.get_monitors()

# NOTE: The album covers are split across the available monitors.
# EDIT 10/12/2021: not anymore!
# coversPerMonitor = int(numCovers/len(monitors))
coversPerMonitor = numCovers
for idx, monitor in enumerate(monitors):

    # Create a name for the wallpaper.
    wallpaperName = "{} - {}x{}".format(idx, monitor.width, monitor.height)
    print(wallpaperName)

    # Calculate the number of columns and rows required to fit the album covers to the screen.
    ratio = monitor.width / monitor.height
    cols = math.floor(math.sqrt(coversPerMonitor * ratio))
    rows = math.floor(coversPerMonitor / cols)

    # Get the subset of covers for this monitor.
    covers = albumCoverPaths[0:coversPerMonitor]
    #del albumCoverPaths[0:coversPerMonitor]
    # Create the wallpaper!
    wallpaper = create_collage(covers, cols=cols, rows=rows)
    wallpaper.save(wallpaperPath + "/" + wallpaperName + ".jpg")
