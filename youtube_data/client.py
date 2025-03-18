import httpx
from typing import List, Dict, Optional, Union
from datetime import datetime
from .models import (
    Video, 
    Channel, 
    PlaylistItem, 
    SearchItem,
    VideoTranscript
)
from .utils import (
    parse_video_output, 
    parse_channel_output, 
    parse_playlist_item,
    parse_search_item,
    create_chunks
)
from .enums import (
    SearchOrderEnum, 
    SearchResourceTypeEnum, 
    SearchVideoDurationEnum, 
    SearchVideoCaptionEnum
)
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter


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

        Args:
            endpoint (str): The endpoint to send the request to.
            params (dict): The query parameters to send with the request.

        Returns:
            dict: The JSON response from the API.
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

        Args:
            url (httpx.URL | str): The URL to hide the API key in.

        Returns:
            str: The URL with the API key replaced by "API_KEY".
        """
        return str(url).replace(self.api_key, "API_KEY")
    
    def get_video_details(self, video_ids: list[str]) -> list[Video] | list[dict]:
        """
        Retrieves the details of a list of videos from the YouTube API.
        Selects attributes from the following parts: statistics, snippet, contentDetails, topicDetails.
        Endpoint video.list costs 1 quota units per call.

        Args:
            video_ids (List[str]): The list of video IDs to retrieve the details for.
        
        Returns:
            List[dict] or dict: The list of Video objects or the raw API response.
        """
        video_ids_chunks = create_chunks(video_ids, 50)

        videos = []
        for chunk in video_ids_chunks:
            params = {"id": ",".join(chunk), "part": "statistics,snippet,contentDetails,topicDetails"}
            response = self._request("videos", params=params)
            response_parsed = [parse_video_output(video) for video in response["items"]]
            videos.extend(response_parsed)
        
        return videos

    def get_channel_details(self, channel_ids: list[str]) -> list[Channel] | list[dict]:
        """
        Retrieves the details of a list of channels from the YouTube API.
        Selects attributes from the following parts: statistics, snippet, contentDetails, topicDetails.
        Endpoint channel.list costs 1 quota units per call.

        Args:
            channel_ids (List[str]): The list of channel IDs to retrieve the details for.

        Returns:
            List[dict] or dict: The list of Channel objects or the raw API response
        """
        channel_ids_chunks = create_chunks(channel_ids, 50)

        channels = []
        for chunk in channel_ids_chunks:
            params={"id": ",".join(chunk), "part": "statistics,snippet,contentDetails,topicDetails"}
            response = self._request("channels", params=params)
            response_parsed = [parse_channel_output(channel) for channel in response["items"]]
            channels.extend(response_parsed)
        
        return channels

    
    def get_playlist_items(
            self, 
            playlist_id: str, 
            max_results: int = 50, 
            max_results_per_page: int = 50
        ) -> list[PlaylistItem]:
        """
        Retrieves the items in a playlist from the YouTube API.
        Endpoint playlistItems.list costs 1 quota units per call.

        Args:
            playlist_id (str): The ID of the playlist to retrieve the items for.
            max_results (int): The maximum number of items to retrieve.
            max_results_per_page (int): The maximum number of items to retrieve per page.

        Returns:
            List[PlaylistItem]: The list of PlaylistItem objects.
        """
        assert max_results_per_page <= 50, "`max_results_per_page` must be less than or equal to 50"
        if max_results < max_results_per_page:
            max_results_per_page = max_results

        playlist_items = []
        params = {
            "playlistId": playlist_id,
            "part": "snippet",
            "maxResults": max_results_per_page,
        }
        while True:
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
            max_results: int = 50,
            **kwargs
        ) -> list[SearchItem]:
        """
        Searches for videos on YouTube using a keyword.
        Endpoint search.list costs 100 quota units per call.

        Args:
            query (str): The search query to use.
            order (SearchOrderEnum): The order to return the results in.
            resource_type (SearchResourceTypeEnum): The type of resource to search for.
            video_duration (SearchVideoDurationEnum): The duration of the videos to search for.
            video_caption (SearchVideoCaptionEnum): The caption type of the videos to search for.
            region_code (str): The region code to search in.
            relevance_language (str): The language to search in.
            published_before (datetime): The date and time to search before.
            published_after (datetime): The date and time to search after.
            max_results (int): The maximum number of results to return.
            **kwargs: Additional query parameters to send with the request.

        Returns:
            List[SearchItem]: The list of SearchItem objects.
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

    @staticmethod
    def get_video_transcript(
        video_id: str, 
        languages: list[str] = ['en'], 
        parse_response: bool = True
    ) -> Union[VideoTranscript | list[dict] | None]:
        """
        Retrieves the transcript of a YouTube video with Youtube-Transcript-API.
        Authentication is not required for this operation.

        Args:
            video_id (str): The ID of the video to retrieve the transcript for.
            languages (List[str]): The list of languages to retrieve the transcript in.
            parse_response (bool): Whether to parse the response into a formatted string.

        Returns:
            str or List[dict] or None: The formatted transcript or the raw API response
        """
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
            if parse_response:
                formatter = TextFormatter()
                transcript = formatter.format_transcript(transcript)
                return VideoTranscript(video_id=video_id, transcript=transcript)
            
            return transcript
            
        except Exception as e:
            return VideoTranscript(video_id=video_id, transcript="transcript not available")
        
    def get_channel_id_from_username(self, username: str) -> Optional[str]:
        """
        Retrieves the channel ID for a given YouTube username.
        
        Args:
            username (str): The YouTube username to look up
            
        Returns:
            Optional[str]: The channel ID if found, None if the channel doesn't exist
            
        Raises:
            ValueError: If the username is empty or invalid
            HTTPError: If the API request fails
        """
        if not username or not isinstance(username, str):
            raise ValueError("Username must be a non-empty string")
            
        params = {
            "forUsername": username, 
            "part": "id"
        }
        
        try:
            response = self._request("channels", params=params)
            items = response.get("items", [])
            return items[0]["id"] if items else None
        except IndexError:
            return None




