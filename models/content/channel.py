from .content import YouTubeAPI
from .video import Video
from .playlist import Playlist


class Channel(YouTubeAPI):
    """
    Class represents a YouTube channel, storing its unique identifier and related attributes. 
    Integrated with the YouTube API, this class provides methods to fetch core details 
    about the channel and its uploaded videos.
    """
    def __init__(self, channel_id: str) -> None:
        super().__init__()
        self.channel_id = channel_id
        self.validate = False

        # validation is turned off to limit api quotas
        if self.validate:
            response = self.get_channel_response(self.channel_id, 'snippet')
            if not response.get('items'):
                raise ValueError(f'Invalid channel ID: {self.channel_id}')
        
        self._channel_name = None  
        self._uploads_playlist_id = None
    
    def __repr__(self) -> str:
        return f"Channel(channel_id={self.channel_id})"

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
    
    @property
    def subscriber_count(self) -> int:
        """
        The number of subscribers to the channel, lazily loaded upon first access.
        """
        if hasattr(self, '_subscriber_count'):
            return self._subscriber_count

        response = self.get_channel_response(self.channel_id, 'statistics')
        self._subscriber_count = int(response['items'][0]['statistics']['subscriberCount'])
        return self._subscriber_count
    
    def info(self) -> tuple:
        """
        Returns in a tuple: channel ID, channel name, channel uploads playlist ID and subscriber count.
        """
        return (self.channel_id, self.channel_name, self.uploads_playlist_id, self.subscriber_count)
    
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
    
    