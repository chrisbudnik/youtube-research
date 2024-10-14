import httpx
from typing import Literal, Optional
from datetime import datetime
from .models import (
    Video, 
    Channel, 
    PlaylistItem, 
    SearchItem
)
from .utils import (
    parse_video_output, 
    parse_channel_output, 
    parse_playlist_item,
    parse_search_item
)
from .enums import (
    SearchOrderEnum, 
    SearchResourceTypeEnum, 
    SearchVideoDurationEnum, 
    SearchVideoCaptionEnum
)


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
    
    def get_playlist_items(
            self, 
            playlist_id: str, 
            max_results: int = 50, 
            max_results_per_page: int = 50
        ) -> list[PlaylistItem]:
        """
        Retrieves the items in a playlist from the YouTube API.
        param: playlist_id: str: The ID of the playlist to retrieve the items for.
        param: max_results: int: The maximum number of items to retrieve.
        param: max_results_per_page: int: The maximum number of items to retrieve per page 
            (affects number of requests).
        return: List[PlaylistItem]: The list of PlaylistItem objects.
        """
        assert max_results_per_page <= 50, "`max_results_per_page` must be less than or equal to 50"

        playlist_items = []
        while True:
            params = {
                "playlistId": playlist_id,
                "part": "snippet",
                "maxResults": max_results_per_page,
            }
            response = self._request("playlistItems", params=params)
            parsed_playlist_items = [parse_playlist_item(item) for item in response["items"]]
            playlist_items.extend(parsed_playlist_items)

            if len(playlist_items) >= max_results or "nextPageToken" not in response:
                break

            params["pageToken"] = response["nextPageToken"]
        return playlist_items
    
    def search(
            self, 
            query: str, 
            order: Optional[SearchOrderEnum] = None,
            resource_type: Optional[SearchResourceTypeEnum] = None,
            video_duration: Optional[SearchVideoDurationEnum] = None,
            video_caption: Optional[SearchVideoCaptionEnum] = None,
            region_code: Optional[str] = "US",
            relevance_language: Optional[str] = "en",
            published_before: Optional[datetime] = None,
            published_after: Optional[datetime] = None,
            max_results: int = 5,
            **kwargs
        ) -> list[SearchItem]:
        """
        Searches for videos on YouTube using a keyword.
        param: query: str: The keyword to search for.
        param: order: SearchOrderEnum: The order in which to return the search results.
        param: resource_type: SearchResourceTypeEnum: The type of resource to search for.
        param: video_duration: SearchVideoDurationEnum: The duration of the videos to search for.
        param: video_caption: SearchVideoCaptionEnum: The caption type of the videos to search for.
        param: region_code: str: The region code to search in.
        param: relevance_language: str: The language to use for the search results.
        param: published_before: datetime: The date and time before which the videos were published.
            The value is converted to RFC 3339 formatted date-time value (1970-01-01T00:00:00Z).
        param: published_after: datetime: The date and time after which the videos were published.
            Same format conversion as `published_before`.
        
        return: List[SearchItem]: The list of SearchItem objects.
        """
        assert max_results <= 50, "`max_results` must be less than or equal to 50"

        params = {
            "q": query,
            "part": "snippet",
            "order": order.value if order else None,
            "type": resource_type.value if resource_type else None,
            "videoDuration": video_duration.value if video_duration else None,
            "videoCaption": video_caption.value if video_caption else None,
            "regionCode": region_code,
            "relevanceLanguage": relevance_language,
            "publishedBefore": published_before.strftime("%Y-%m-%dT%H:%M:%S") if published_before else None,
            "publishedAfter": published_after.strftime("%Y-%m-%dT%H:%M:%S") if published_after else None,
            "maxResults": max_results,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None}

        items = []
        while True:
            response = self._request("search", params=params)
            search_items = [parse_search_item(item) for item in response["items"]]
            items.extend(search_items)

            if len(items) >= max_results or "nextPageToken" not in response:
                break
            params["pageToken"] = response["nextPageToken"]

        return items


    def get_channel_id_from_username(self, username: str) -> str:
        params={"forUsername": username, "part": "statistics,snippet,contentDetails,topicDetails"}
        response = self._request("channels", params=params)
        return response




