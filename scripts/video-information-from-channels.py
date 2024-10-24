import sys
import os

# Add the parent directory to sys.path (correct import)
parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
sys.path.insert(0, parent_dir)

# ----------------------------- #
from youtube_data import YouTube
from api_secret import api_key 

CHANNEL_IDS = ["UCV6KDgJskWaEckne5aPA0aQ"]

with YouTube(api_key) as yt:
    channels = yt.get_channel_details(channel_ids=CHANNEL_IDS)
    for channel in channels:
        playlist_items = yt.get_playlist_items(channel.uploads_playlist_id)

        with open(f"data/{channel.channel_title}.txt", "w") as f:
            for item in playlist_items:
                f.write(f"{channel.channel_id}, {channel.uploads_playlist_id}, {item.video_id}\n")