import httpx
#from typing import List, Dict
from .models import Video, Channel
from .utils import parse_video_output, parse_channel_output


class YouTube:
    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, api_key):
        self.api_key = api_key
        self._httpx_client = None

    @property
    def httpx_client(self):
        if self._httpx_client is None:
            self._httpx_client = httpx.Client()
        return self._httpx_client

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._httpx_client is not None:
            self._httpx_client.close()
            self._httpx_client = None

    def _request(self, endpoint: str, params: dict = {}) -> dict:
        """
        Sends a GET request to the YouTube API and returns the response.
        param: endpoint: str: The API endpoint to send the request to.
        param: params: dict: The query parameters to include in the request.
        return: dict: The JSON response from the API.
        """
        params['key'] = self.api_key
        url = f"{self.BASE_URL}/{endpoint}"

        try:
            response = self.httpx_client.get(url, params=params)
            print(f"YouTube API Request -> {self._hide_api_key(response.url)}")
            response.raise_for_status() 

        except httpx.HTTPStatusError as e:
            print(f"HTTP Error: {self._hide_api_key(e)}")
            raise

        return response.json()
    
    def _hide_api_key(self, url: httpx.URL | str) -> str:
        """
        Hides the API key in the URL (for logging purposes).
        param: url: httpx.URL: The URL to hide the API key in.
        return: str: The URL with the API key replaced by "API_KEY".
        """
        return str(url).replace(self.api_key, "API_KEY")
    
    def get_video_details(self, video_ids: list[str], parsed_response: bool = True) -> list[Video] | list[dict]:
        """
        Retrieves the details of a list of videos from the YouTube API.
        Selects attributes from the following parts: statistics, snippet, contentDetails, topicDetails.
        param: video_ids: List[str]: The list of video IDs to retrieve the details for.
        param: parsed_response: bool: Whether to parse the response into Video objects.
        return: List[Video] or dict: The list of Video objects or the raw response.
        """
        params={"id": ",".join(video_ids), "part": "statistics,snippet,contentDetails,topicDetails"}
        response = self._request("videos", params=params)
        if not parsed_response:
            return response["items"]
        
        return [parse_video_output(video) for video in response["items"]]

    def get_channel_details(self, channel_ids: list[str], parsed_response: bool = True) -> list[Channel] | list[dict]:
        """
        Retrieves the details of a list of channels from the YouTube API.
        Selects attributes from the following parts: statistics, snippet, contentDetails, topicDetails.
        param: channel_ids: List[str]: The list of channel IDs to retrieve the details for.
        param: parsed_response: bool: Whether to parse the response into Channel objects.
        return: List[dict] or dict: 
        """
        params={"id": ",".join(channel_ids), "part": "statistics,snippet,contentDetails,topicDetails"}
        response = self._request("channels", params=params)
        if not parsed_response:
            return response["items"]
        
        return [parse_channel_output(channel) for channel in response["items"]]
    
    def get_channel_id_from_username(self, username: str) -> str:
        params={"forUsername": username, "part": "statistics,snippet,contentDetails,topicDetails"}
        response = self._request("channels", params=params)
        return response

    def get_playlist_details(self, playlist_id: str):
        params={"playlistId": playlist_id, "part": "snippet,contentDetails"}
        return self._request("playlistItems", params=params)
    




