from datetime import datetime
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
