#!/usr/bin/env python3

from src.utils import *
from src.fetch import fetch_playlist, fetch_songs
from src.downloader import downloader
from datetime import datetime
import argparse
import sys
import os


# Argument Parsing
parser = argparse.ArgumentParser(description="Sync youtube playlist with local machine.")
parser.add_argument("-o", "--output-folder", metavar="PATH", type=str, help="Override default or config output folder")
parser.add_argument("-f", "--force-update", action="store_true", help="Force Redownload the entire playlist.")
argv = parser.parse_args()

folder = ""
if argv.output_folder:
    folder = os.path.expanduser(argv.output_folder)

# Config location
MUSIC_DIRECTORY = folder or os.path.expanduser("~/Music")
PLAYLIST_FILE = os.path.expanduser("~/.ypsync/yplaylists")
SYNC_FILE = os.path.expanduser("~/.ypsync/sync_status.json")
DEVELOPER_KEY = os.environ["YOUTUBE_TOKEN"] # You can replace this with your key
ensure_folder(MUSIC_DIRECTORY) # Create MUSIC_DIRECTORY if it does not exists


def is_present(playlist_title:str) -> bool:
    playlist_folder = os.path.join(MUSIC_DIRECTORY, playlist_title)
    return os.path.exists(playlist_folder)


def update(playlist: dict):
    playlist_folder = os.path.join(MUSIC_DIRECTORY, f"{playlist['title']} (Youtube)")
    
    local_songs = [os.path.join(playlist_folder, video) for video in os.listdir(playlist_folder)]
    global_songs = fetch_songs(playlist["id"], DEVELOPER_KEY)
    
    local_song_IDs = {get_video_id(song) for song in local_songs}
    global_song_IDS = {video['id'] for video in global_songs}

    # Set Algebra Rocks
    removed = local_song_IDs - global_song_IDS
    added = global_song_IDS - local_song_IDs
    net_change = local_song_IDs ^ global_song_IDS

    
    if len(net_change) == 0:
        print("No changes from upstream detected. Nothing done.")
        return
    else:
        print("Changes detected! {} songs added and {} songs removed in upstream. Syncing...".format(len(added), len(removed)))
        # Remove songs removed from upstream
        index = dict(zip([get_video_id(song) for song in local_songs], local_songs))
        for song in removed:
            print("Removing %s..." % os.path.basename(index[song]) )
            os.remove(index[song])

        # Add songs added in upstream
        videos = []
        for song in global_songs:
            if song['id'] in list(added):
                videos.append(song)
        
        downloader(videos, playlist, MUSIC_DIRECTORY)


def main():
    playlists = fetch_playlist(playlist_file(PLAYLIST_FILE), DEVELOPER_KEY)

    ensure_sync_file(SYNC_FILE)
    sync_prev = fetch_sync_file(SYNC_FILE)

    for playlist in playlists:
        if playlist['id'] in list(sync_prev.keys()) and os.path.exists(os.path.join(MUSIC_DIRECTORY, f"{playlist['title']} (Youtube)")) and not argv.force_update:
            # update
            print("The playlist '%s' has been previously synced. Detecting changes..." % playlist["title"])
            update(playlist)
            sync_prev[playlist["id"]] = {"lastUpdated": datetime.now().strftime("%d-%m-%YT%H:%M:%S")}
        else:
            # create
            delete_playlist(MUSIC_DIRECTORY, playlist['title']) # remove already existing folder incase
            if argv.force_update:
                print("Redownloading playlist '%s'.." % playlist['title'])
            else:
                print("The playlist '%s' has not been previously synced. Syncing..." % playlist["title"])
            videos = fetch_songs(playlist["id"], DEVELOPER_KEY)
            sync_prev[playlist["id"]] = {"lastUpdated": datetime.now().strftime("%d-%m-%YT%H:%M:%S")} # To start from where it crashed instead of starting over in case of a interuption.
            update_sync_file(sync_prev, SYNC_FILE)
            downloader(videos, playlist, MUSIC_DIRECTORY)
        
    update_sync_file(sync_prev, SYNC_FILE)

    return 0

if __name__ == "__main__":
    main()