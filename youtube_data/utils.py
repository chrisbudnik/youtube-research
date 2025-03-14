import re
from datetime import datetime
from .models import Video, Channel, PlaylistItem, SearchItem


def parse_datetime_from_string(date_string: str) -> datetime:
    """
    Parses a datetime object from a string.
    param: date_string: str: The string representation of the date.
    return: datetime: The parsed datetime object.

    Example: '2016-12-25T07:48:56Z'
    """
    try:
        date_formatted = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
    except Exception as e:
        date_formatted = date_string
    return date_formatted

def convert_iso8601_duration_to_seconds(duration: str) -> int:
    """
    Converts an ISO8601 duration string to seconds.
    param: duration: str: The ISO8601 duration string.
    return: int: The duration in seconds.

    Example: 'PT14M8S'
    """
    pattern = re.compile(r'P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
    match = pattern.match(duration)

    if not match:
        raise ValueError("Invalid ISO8601 duration format")

    days = int(match.group(1)) if match.group(1) else 0
    hours = int(match.group(2)) if match.group(2) else 0
    minutes = int(match.group(3)) if match.group(3) else 0
    seconds = int(match.group(4)) if match.group(4) else 0

    return days * 86400 + hours * 3600 + minutes * 60 + seconds

def parse_video_output(video: dict) -> Video:
    """
    Parses the video response from the YouTube API.
    param: video: dict: The video response from the YouTube API.
    return: Video: The parsed video response.
    """

    parsed_video = {
        "video_id": video["id"],
        "title": video["snippet"]["title"],
        "description": video["snippet"]["description"],
        "channel_id": video["snippet"]["channelId"],
        "channel_title": video["snippet"]["channelTitle"],
        "published_at": parse_datetime_from_string(video["snippet"]["publishedAt"]),
        "duration": convert_iso8601_duration_to_seconds(video["contentDetails"]["duration"]),
        "tags": video["snippet"].get("tags", []),
        "category_id": int(video["snippet"]["categoryId"]),
        "view_count": int(video["statistics"]["viewCount"]),
        "like_count": int(video["statistics"].get("likeCount", 0)),
        "dislike_count": int(video["statistics"].get("dislikeCount", 0)),
        "comment_count": int(video["statistics"].get("commentCount", 0)),

    }
    return Video(**parsed_video)

def parse_channel_output(channel: dict) -> Channel:
    """
    Parses the channel response from the YouTube API.
    param: channel: dict: The channel response from the YouTube API.
    return: Channel: The parsed channel response.
    """
    parsed_channel = {
        "channel_id": channel["id"],
        "channel_title": channel["snippet"]["title"],
        "description": channel["snippet"]["description"],
        "custom_url": channel["snippet"].get("customUrl", ""),
        "published_at": parse_datetime_from_string(channel["snippet"]["publishedAt"]),
        "uploads_playlist_id": channel["contentDetails"]["relatedPlaylists"]["uploads"],
        "view_count": int(channel["statistics"].get("viewCount", 0)),
        "subscriber_count": int(channel["statistics"].get("subscriberCount", 0)),
        "video_count": int(channel["statistics"].get("videoCount", 0)),
    }
    return Channel(**parsed_channel)

def parse_playlist_item(playlist_item: dict) -> PlaylistItem:
    """
    Parses the playlist item response from the YouTube API.
    param: playlist_item: dict: The playlist item response from the YouTube API.
    return: PlaylistItem: The parsed playlist item response.
    """
    parsed_playlist_item = {
        "playlist_id": playlist_item["snippet"]["playlistId"],
        "channel_id": playlist_item["snippet"]["channelId"],
        "video_id": playlist_item["snippet"]["resourceId"]["videoId"],
        "position": int(playlist_item["snippet"]["position"]),
    }
    return PlaylistItem(**parsed_playlist_item)

def parse_search_item(search_item: dict) -> SearchItem:
    """
    Parses the search item response from the YouTube API.
    param: search_item: dict: The search item response from the YouTube API.
    return: SearchItem: The parsed search item response.
    """
    parsed_search_item = {
        "resource_type": search_item["id"]["kind"],
        "video_id": search_item["id"].get("videoId"),
        "channel_id": search_item["snippet"].get("channelId"),
        "playlist_id": search_item["id"].get("playlistId"),
    }
    return SearchItem(**parsed_search_item)

def create_chunks(lst, n):
    """
    Manages requests limits by creating chunks of youtube object ids.

    Args:
        lst: list: The list of object ids.
        n: int: The number of objects per chunk.
    
    Returns:
        list: The list of chunks.
    """
    chunks = []
    for i in range(0, len(lst), n):
        chunks.append(lst[i:i+n])
    return chunks
