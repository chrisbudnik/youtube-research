from typing import List, Tuple
from .content import YouTubeAPI
from .video import Video


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