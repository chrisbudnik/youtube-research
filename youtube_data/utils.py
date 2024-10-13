
from datetime import datetime
from typing import Dict
from .models import Video


def parse_datetime_from_string(date_string: str) -> datetime:
    """
    Parses a datetime object from a string.
    param: date_string: str: The string representation of the date.
    return: datetime: The parsed datetime object.

    Example: '2016-12-25T07:48:56Z'
    """
    return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")

def convert_iso8601_duration_to_seconds(duration: str) -> int:
    """
    Converts an ISO8601 duration string to seconds.
    param: duration: str: The ISO8601 duration string.
    return: int: The duration in seconds.

    Example: 'PT14M8S'
    """

def parse_video_output(video: Dict) -> Dict:
    """
    Parses the video response from the YouTube API.
    param: video: dict: The video response from the YouTube API.
    return: dict: The parsed video response.
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
