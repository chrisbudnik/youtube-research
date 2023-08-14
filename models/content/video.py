import re
from dateutil.parser import parse
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi
from .content import YouTubeAPI


class Video(YouTubeAPI):
    """
    Represents a YouTube video, encapsulating its unique identifier and core attributes. 
    Through integration with the YouTube API, this class furnishes a comprehensive suite 
    of methods designed to retrieve a wide range of video details. These details encompass 
    basic metadata like the video's name, channel, and publication date, as well as more 
    granular statistics such as views, likes, and comments. Additionally, it provides 
    functionalities to fetch and process the video transcript, making it a versatile tool 
    for diverse YouTube video analyses.
    """

    SHORTS_MAX_LENGTH = 60
    
    def __init__(self, video_id:str) -> None:
        super().__init__()
        self.video_id = video_id
        self.validate = False

        # check if video exists, else return error - turned off to save api quotas
        if self.validate:
            response = self.get_video_response(self.video_id, 'snippet')
            if not response.get('items'):
                raise ValueError(f'Invalid video ID: {self.video_id}')
        
        self._video_name = None 
        self._video_length = None 
        self._channel_id = None

    def __repr__(self):
        return f"Video(video_id={self.video_id})"

    def __eq__(self, other):
        if isinstance(other, Video):
            return self.video_id == other.video_id
        return False

    def __hash__(self):
        return hash(self.video_id)
    
    def __len__(self):
        """
        Returns the video's length in seconds.
        """
        if self._video_length is None:
            self._video_length = self.get_video_properties()['length']
        return self._video_length

    @property
    def video_name(self):
        """
        Name of the video. Lazily loaded upon first access.
        """
        if self._video_name is None:
            self._video_name = self.get_video_properties()['video_name']
        return self._video_name
    
    @property
    def channel_id(self):
        """
        ID of the channel the video belongs to. Lazily loaded upon first access.
        """
        if self._channel_id is None:
            self._channel_id= self.get_video_properties()['channel_id']
        return self._channel_id
    
    
    def get_video_properties(self) -> dict:
        """
        Fetch and return detailed properties of the video, including its name, channel, 
        publication date, length, type, license, etc.
        """
        response = self.get_video_response(self.video_id, 'statistics, contentDetails, snippet, status')

        video_length = self._convert_time_to_seconds(response['items'][0]['contentDetails']['duration'])

        video_stats = {
            "video_id": self.video_id,
            "video_name": response['items'][0]['snippet']['title'],
            "channel_id": response['items'][0]['snippet']['channelId'],
            "channel_name": response['items'][0]['snippet']['channelTitle'],
            "category_id": response['items'][0]['snippet']['categoryId'],
            "published_at": self._parse_date(response['items'][0]['snippet']['publishedAt']),
            "length": video_length,
            "type": ("shorts" if video_length <= self.SHORTS_MAX_LENGTH else "video"),
            "license": "Standard License" if response['items'][0]['status']['license'] == 'youtube' else "Creative Commons",
            "made_for_kids": response['items'][0]['status']['madeForKids'],
            "user_tags": response['items'][0]['snippet'].get('tags', []),
            "description": response['items'][0]['snippet']['description'],
        }
        return video_stats
    
    def get_video_stats(self) -> dict[str: str]:
        """
        Fetch and return statistics of the video, including views, likes, and comments.
        """
        response = self.get_video_response(self.video_id, 'statistics, contentDetails')
        
        video_stats = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "video_id": self.video_id,
            "views": response['items'][0]['statistics']['viewCount'],
            "likes": response['items'][0]['statistics']['likeCount'],
            "comments": response['items'][0]['statistics'].get('commentCount', 0),
        }
        return video_stats

    def get_video_transcript(self):
        """
        Fetch and return the transcript of the video in a consolidated string format.
        """
        id = self.video_id[:11]
        transcript = YouTubeTranscriptApi.get_transcript(id)
        full_transcript = {"transcript": " ".join([part['text'] for part in transcript])}
        return full_transcript  

    @staticmethod
    def _convert_time_to_seconds(time_string: str) -> int:
        """
        Convert a given duration format (used by YouTube) to total seconds.
        """
        pattern = r'PT((\d+)H)?((\d+)M)?((\d+)S)?'
        match = re.match(pattern, time_string)

        hours = int(match.group(2)) if match.group(2) else 0
        minutes = int(match.group(4)) if match.group(4) else 0
        seconds = int(match.group(6)) if match.group(6) else 0

        total_seconds = hours * 3600 + minutes * 60 + seconds
        return total_seconds

    @staticmethod
    def _parse_date(date_string: str) -> str:
        """
        Convert a given date string to standard ISO format.
        """
        return parse(date_string).date().isoformat()