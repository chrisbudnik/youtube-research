# **YouTube Data Module**

A simple module to interact with the YouTube Data API and retrieve video transcripts. 
Responses are packed into **Pydantic models** for seamless data handling. 
The module uses raw HTTP requests with **httpx** and optimizes API costs by allowing batch operations — 
for example, fetching multiple video details at once.

---

## 🌟 Overview

This module provides an easy-to-use interface for:

- Fetching details about videos, channels, and playlists.
- Searching for videos based on queries.
- Retrieving video transcripts.
- Converting YouTube usernames to channel IDs.

---

## 📹 Get Video Details

Retrieve details of one or more YouTube videos.

```python
from youtube_data.client import YouTube

api_key = 'YOUR_API_KEY'
youtube = YouTube(api_key)

video_ids = ['VIDEO_ID_1', 'VIDEO_ID_2']
videos = youtube.get_video_details(video_ids)

for video in videos:
    print(f"Title: {video.title}")
    print(f"Views: {video.view_count}")
    print(f"Duration: {video.duration}")
```

---

## 👥 Get Channel Details

Fetch details about one or more YouTube channels.

```python
channel_ids = ['CHANNEL_ID_1', 'CHANNEL_ID_2']
channels = youtube.get_channel_details(channel_ids)

for channel in channels:
    print(f"Channel Title: {channel.title}")
    print(f"Subscribers: {channel.subscriber_count}")
    print(f"Upload playlist ID: {channel.uploads_playlist_id}")
```

---

## 📄 Get Playlist Items

Retrieve all items from a specific playlist.

```python
playlist_id = 'PLAYLIST_ID'
playlist_items = youtube.get_playlist_items(playlist_id)

for item in playlist_items:
    print(f"Video Title: {item.title}")
    print(f"Video ID: {item.video_id}")
```

---

## 🔍 Search Videos

Search for videos on YouTube based on a query.

```python
from youtube_data.client import YouTube
from youtube_data.enums import SearchOrderEnum, SearchResourceTypeEnum

api_key = 'YOUR_API_KEY'
youtube = YouTube(api_key)

search_results = youtube.search(
    query='Python tutorials',
    order=SearchOrderEnum.RELEVANCE,
    resource_type=SearchResourceTypeEnum.VIDEO,
    max_results=10
)

for item in search_results:
    print(f"Video ID: {item.video_id}")
    print(f"Channel ID: {item.channel_id}")
```

---

## 💬 Get Video Transcript

Retrieve the transcript of a YouTube video (Youtube-Transcript-API wrapper).

```python
video_id = 'VIDEO_ID'
transcript = youtube.get_video_transcript(video_id, parse_response=True)

print(transcript)
```

---

## 📊 Data Collection Strategies
This module supports various data collection strategies to efficiently gather information:

- Channel-Centric Approach: Start with a list of channel IDs, retrieve their playlist IDs, then fetch video IDs from these playlists, and finally collect detailed video information.

- Keyword-Based Channel Discovery: Search for channels based on specific keywords or topics, obtain their channel IDs from the search results, and proceed as in the first approach to gather video data.

- Direct Video Search: Use keywords or topics to search for videos directly, get video IDs from the search results, and then retrieve detailed information about these videos.

---

## 💡 Use Cases

- **Content Analysis**: Gather data about videos and channels for analysis.
- **Playlist Management**: Retrieve and manage playlist items.
- **Automated Searching**: Automate the process of searching YouTube for specific content.
- **Transcription Services**: Fetch video transcripts for subtitling or analysis.
- **User Data Retrieval**: Convert usernames to channel IDs for further data retrieval.


---

## 📄 Notes

- An API key is required to use the YouTube Data API features. You can obtain one from the [Google Developers Console](https://console.developers.google.com/).
- The `youtube_transcript_api` does not require authentication.
- This module is not yet packaged; you can use the code directly in your project.

---

## ⚙️ Dependencies

- `httpx`
- `youtube_transcript_api`

---

Feel free to contribute to this module or report any issues!