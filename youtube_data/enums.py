from enum import Enum


class SearchOrderEnum(Enum):
    DATE = "date"
    RATING = "rating"
    RELEVANCE = "relevance"
    TITLE = "title"
    VIDEO_COUNT = "videoCount"
    VIEW_COUNT = "viewCount"

class SearchResourceTypeEnum(Enum):
    VIDEO = "video"
    CHANNEL = "channel"
    PLAYLIST = "playlist"

class SearchVideoDurationEnum(Enum):
    ANY = "any"
    LONG = "long"
    MEDIUM = "medium"
    SHORT = "short"

class SearchVideoCaptionEnum(Enum):
    ANY = "any"
    CLOSED_CAPTION = "closedCaption"
    NONE = "none"

class SearchVideoLicenseEnum(Enum):
    ANY = "any"
    CREATIVE_COMMONS = "creativeCommon"
    YOUTUBE = "youtube"

