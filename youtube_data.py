import re
from dateutil.parser import parse
from datetime import datetime, timezone, timedelta
from typing import Literal, Optional, Union, List, Tuple
from tqdm import tqdm
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from configuration import Config


class YouTubeAPI:
    """
    A class to interact with the YouTube Data API v3, providing methods to fetch video details, 
    channel details, search results, and playlist items.
    """
    def __init__(self):
        self.youtube = build(Config.YOUTUBE_API_SERVICE_NAME, Config.YOUTUBE_API_VERSION, developerKey=Config.DEVELOPER_KEY)

    def get_video_response(self, video_id: str, part: str):
        return self.youtube.videos().list(
            part=part,
            id=video_id
        ).execute()

    def get_channel_response(self, channel_id: str, part: str):
        return self.youtube.channels().list(
            part=part,
            id=channel_id
        ).execute()
    
    def get_search_response(
            self, 
            key: str, 
            part: str,
            type: Literal["video", "channel", "playlist", "movie"],
            order_by: Literal["viewCount", "relevance", "date"],
            max_results: int,
            published_after = None
            ):
        
        return self.youtube.search().list(
                q=key,
                type=type,
                order=order_by,
                publishedAfter=published_after,
                part=part,
                maxResults=max_results
            ).execute()
    
    def get_playlist_response(
            self,
            playlist_id: str,
            part: str,
            max_results: int = 50,
            page_token = None
        ):

        return self.youtube.playlistItems().list(
                part=part,
                playlistId=playlist_id,
                maxResults=max_results,
                pageToken=page_token
            ).execute()


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
    
    def __init__(self, video_id:str):
        super().__init__()
        self.video_id = video_id

        # check if video exists, else return error
        response = self.get_video_response(self.video_id, 'snippet')
        if not response.get('items'):
            raise ValueError(f'Invalid video ID: {self.video_id}')
        
        self._video_name = None 
        self._video_length = None 
        self._channel_id = None

    def __repr__(self):
        return f"Video(video_id={self.video_id}, video_name={self.video_name})"

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
    

class Playlist(YouTubeAPI):
    """
    Represents a YouTube playlist, describing its unique identifier and core attributes. 
    Through integration with the YouTube API, this class provides methods to retrieve essential 
    details about the playlist and its constituent videos.
    """
    def __init__(self, playlist_id: str):
        super().__init__()
        self.playlist_id = playlist_id

        response = self.get_playlist_response(self.playlist_id, 'snippet')
        if not response.get('items'):
            raise ValueError(f'Invalid playlist ID: {self.playlist_id}')

    def __repr__(self):
        return f"Playlist(playlist_id={self.playlist_id})"

    def __eq__(self, other):
        if isinstance(other, Playlist):
            return self.playlist_id == other.playlist_id
        return False

    def __hash__(self):
        return hash(self.playlist_id)
    
    def get_playlist_videos(
            self, 
            max_results: int = 50, 
            page_token: str = None
        ) -> Tuple[List[Video], str]: 
        """
        Fetches videos contained in the playlist, up to the specified max_results. 
        It can also continue from a specific page in case of paginated results, using the page_token. 
        Returns a tuple containing a list of Video objects and a token for the next page of results.
        """
        
        playlist_response = self.get_playlist_response(self.playlist_id, 'contentDetails', max_results, page_token)

        video_ids = [Video(item['contentDetails']['videoId']) for item in playlist_response['items']]
        next_page_token = playlist_response.get('nextPageToken')

        return video_ids, next_page_token
    

# what if channel does not have playlist?
class Channel(YouTubeAPI):
    """
    Class represents a YouTube channel, storing its unique identifier and related attributes. 
    Integrated with the YouTube API, this class provides methods to fetch core details 
    about the channel and its uploaded videos.
    """
    def __init__(self, channel_id: str):
        super().__init__()
        self.channel_id = channel_id

        response = self.get_channel_response(self.channel_id, 'snippet')
        if not response.get('items'):
            raise ValueError(f'Invalid channel ID: {self.channel_id}')
        
        self._channel_name = None  
        self._uploads_playlist_id = None
    
    def __repr__(self):
        return f"Channel(channel_id={self.channel_id}, channel_name={self.channel_name})"

    def __eq__(self, other):
        if isinstance(other, Channel):
            return self.channel_id == other.channel_id
        return False
    
    def __hash__(self):
        return hash(self.channel_id)

    @property
    def channel_name(self) -> str:
        """
        The name of the channel, lazily loaded upon first access.
        """
        if self._channel_name is None: 
            response = self.get_channel_response(self.channel_id, 'snippet')
            self._channel_name = response['items'][0]['snippet']['title']
        return self._channel_name
    
    @property
    def uploads_playlist_id(self) -> str:
        """
        The ID of the playlist containing all the uploads of the channel, 
        lazily loaded upon first access.
        """
        if self._uploads_playlist_id is None: 
            self._uploads_playlist_id = self.get_playlist_id(type="uploads")
        return self._uploads_playlist_id
    
    def get_channel_videos(self, max_results=5) -> list[Video]:
        """
        Fetches a specified number of videos uploaded to the channel. 
        Returns a list of Video objects representing the uploaded videos.
        """
        videos = []
        next_page_token = None
        playlist = Playlist(self.uploads_playlist_id)

        while True:
            max_results_chunk = min(max_results - len(videos), 50)  
            if max_results_chunk <= 0:
                break  
            
            videos_to_add, next_page_token = playlist.get_playlist_videos(max_results=max_results_chunk, page_token=next_page_token)
            videos.extend(videos_to_add)

        return videos

    def get_playlist_id(self, type: str = "uploads") -> str:
        """
        Retrieves the ID of a specific type of playlist associated with the channel, 
        e.g., "uploads" for the channel's uploaded videos.
        """
        channel_response = self.get_channel_response(self.channel_id, 'contentDetails')
        playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists'][type]
        return playlist_id
    

class YouTubeDataCollector:
    """
    YoutubeDataCollector class is responsibe for gathering data via custom interface for
    YouTube api. It provides two methods for data collection: collect_data_from_channel and collect_data_from_videos.
    """
    def __init__(self, channel_ids: Optional[list[str]] = None, video_ids: Optional[list[str]] = None):
        self.channel_ids = channel_ids or []
        self.video_ids = video_ids or []

    def collect_data_from_channels(self, max_videos: int) -> list[dict]:
        """
        Collects data from provieded channel ids. Designed for static data, method combines video properties and 
        video transcrip. Results are saved in dictionary format.
        """
        all_video_data = []

        if not len(self.channel_ids):
            raise ValueError("Methods requires channel_ids to collect data.")

        for channel_id in tqdm(self.channel_ids, desc="Processing videos from channel ids"):
            channel = Channel(channel_id)
            channel_videos = channel.get_channel_videos(max_videos)

            for video in channel_videos:
                video_data = video.get_video_properties() | video.get_video_transcript()
                all_video_data.append(video_data)

        return all_video_data

    def collect_data_from_videos(self) -> list:
        """
        Collects data from video ids. Designed for dynamic data (data that is changing over time).
        Results are saved in dictionary format.
        """
        all_video_data = []

        if not len(self.video_ids):
            raise ValueError("Methods requires video_ids to collect data.")

        for video_id in tqdm(self.video_ids, desc="Processing videos from video ids"):
            video = Video(video_id)
            video_data = video.get_video_stats()
            all_video_data.append(video_data)

        return all_video_data
    

class YouTubeSearch(YouTubeAPI):
    """
    The YouTubeSearch class enables targeted search capabilities on YouTube by 
    leveraging the functionalities provided by the YouTubeAPI. It allows users to perform 
    specific keyword-based searches for videos and channels, gather top-ranking channels 
    based on recent video performance, and identify channels whose names exactly match given keywords.
    """
    def __init__(self, keywords: list[str]):
        super().__init__()
        self.keywords = keywords

    def execute_search(
            self, 
            type: Literal["video", "channel", "playlist", "movie"], 
            max_results: int = 1, 
            published_after = None, 
            order_by: Literal["viewCount", "relevance", "date"] = 'relevance'
        ) -> Union[List[Video], List[Channel]]:
        """
        Executes a search on YouTube based on given criteria (provided keywords). 
        Ability to specify number of results per term with max_results and publishing 
        timeframe thanks to published_after. Fetch results based on selected order method:
        view count, relevance and date. Currently only supports 'video' and 'channel' types.
        """

        if type in ["playlist", "movie"]:
            raise NotImplementedError(f"Searching for {type} is not implemented yet")
        
        if type not in ["video", "channel"]:
            raise KeyError("Only types: 'video' and 'channel' are supported")

        all_search_data = []

        for key in self.keywords:
            search_response = self.get_search_response(key, 'id,snippet', type, order_by, max_results, published_after)

            for item in search_response.get('items', []):
                    result = item['id'][f'{type}Id']
                    if type == "video": 
                        all_search_data.append(Video(result))
                    else: 
                        all_search_data.append(Channel(result))

        return all_search_data

    def collect_exact_terms(self) -> List[Channel]:
        """
        Searches for channels using keywords and returns channel IDs that exactly match the keywords.
        """
        search_results = self.execute_search('channel')

        channel_ids = []
        for key, channel in zip(self.keywords, search_results):
            if key.lower() == channel.channel_name.lower():
                channel_ids.append(channel.channel_id)
        
        return channel_ids
            
    def collect_best_ranking_channels(
            self, 
            max_results: int = 1, 
            order_by: Literal["viewCount", "relevance", "date"] = 'viewCount',
            only_unique = True
        ) -> List[Channel]:
        """
        Collects the top-ranking channels based on videos published in the last 30 days, 
        optionally ensuring uniqueness. Ability to specify the limit of results per keyword 
        with max_results. Recommended order_by value is viewCount since relevance does not 
        guarante general best ranking results.
        """

        ranking_start_date = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        best_ranking_videos = self.execute_search(type='video', max_results=max_results, published_after=ranking_start_date, order_by=order_by)

        best_ranking_channels = [Channel(video.channel_id) for video in best_ranking_videos]
               
        if only_unique:
            best_ranking_channels = list(set(best_ranking_channels))

        return best_ranking_channels
    