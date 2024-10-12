from datetime import datetime
from pydantic import BaseModel


class Video(BaseModel):
    """
    Video is a template for defining operations to be applied to a DataFrame.
    """
    video_id: str
    title: str
    description: str
    channel_id: str
    channel_title: str
    published_at: datetime
    duration: int
    tags: list
    category_id: int
    view_count: int
    like_count: int
    dislike_count: int
    comment_count: int
