from tqdm import tqdm
from datetime import datetime, timezone, timedelta
from typing import Literal, Union, List
from models.content import Video, Channel, Playlist, YouTubeAPI


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

        for key in tqdm(self.keywords, desc="Collecting results for keyword..."):
            search_response = self.get_search_response(key, 'id, snippet', type, order_by, max_results, published_after)

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
        not_found_keywords = []

        for key, channel in zip(self.keywords, search_results):
            if key.lower() == channel.channel_name.lower():
                channel_ids.append(channel.channel_id)
            else: 
                not_found_keywords.append(key)

        if not_found_keywords:
            print(f'Warning: some of the provided keywords were not found: {not_found_keywords}')
        
        return [Channel(id) for id in channel_ids]
            
    def collect_best_ranking_channels(
            self, 
            max_results: int = 1, 
            timeframe: int = 30,
            order_by: Literal["viewCount", "relevance", "date"] = 'viewCount',
            only_unique = True
        ) -> List[Channel]:
        """
        Collects the top-ranking channels based on videos published in the last 30 days, 
        optionally ensuring uniqueness. Ability to specify the limit of results per keyword 
        with max_results. Recommended order_by value is viewCount since relevance does not 
        guarante general best ranking results.
        """

        ranking_start_date = (datetime.now(timezone.utc) - timedelta(days=timeframe)).strftime("%Y-%m-%dT%H:%M:%SZ")
        best_ranking_videos = self.execute_search(type='video', max_results=max_results, published_after=ranking_start_date, order_by=order_by)

        best_ranking_channels = [Channel(video.channel_id) for video in best_ranking_videos]
               
        if only_unique:
            best_ranking_channels = list(set(best_ranking_channels))

        return best_ranking_channels