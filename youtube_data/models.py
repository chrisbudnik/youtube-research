from datetime import datetime
from typing import Literal, Optional
from enum import Enum
from pydantic import BaseModel


class Video(BaseModel):
    """
    Video is a model representing a YouTube video.
    """
    video_id: str
    title: str
    description: str
    channel_id: str
    channel_title: str
    published_at: datetime
    duration: int
    tags: list[str]
    category_id: int
    view_count: int
    like_count: int
    dislike_count: int
    comment_count: int

class Channel(BaseModel):
    """
    Channel is a model representing a YouTube channel.
    """
    channel_id: str
    channel_title: str
    description: str
    custom_url: str
    published_at: datetime
    uploads_playlist_id: str
    view_count: int
    subscriber_count: int
    video_count: int

class PlaylistItem(BaseModel):
    """
    PlaylistItem is a model representing an item in a YouTube playlist.
    """
    playlist_id: str
    channel_id: str
    video_id: str
    position: int


class SearchItem(BaseModel):
    """
    SearchItem is a model representing an item in a YouTube search result.
    """
    resource_type: Literal["youtube#video", "youtube#channel", "youtube#playlist"]
    video_id: Optional[str] = None
    channel_id: Optional[str] = None
    playlist_id: Optional[str] = None

