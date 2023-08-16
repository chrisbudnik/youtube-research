import sys
sys.path.append('/Users/chrisbudnik/Desktop/Projects/youtube-research')

import csv
from tqdm import tqdm

from models.search import YouTubeSearch
from databases.bigquery_connector import BigQueryConnector
from databases.bigquery_connector import BigQueryTableNames

# For the purpose of this tutorial, search terms were generted by chatGPT for personal finance niche.
# Example terms: 'Budgeting for beginners', 'Investing for millennials'.

# Parsing search terms saved in .txt file.
with open('/Users/chrisbudnik/Desktop/Projects/youtube-research/datasets/search-terms/search-online-business.txt', 'r') as file:
    search_terms = [line.strip().strip('"')  for line in file]

# To aviod surpassing api limits, only top 5 search terms were selected
sample = search_terms[:60]

# Crating an instance of YoutubeSearch
search = YouTubeSearch(keywords=sample)

# Max results is set to 10 (youtube api limit is 50)
results = search.collect_best_ranking_channels(max_results = 50, 
                                               timeframe=360,
                                               order_by="viewCount", 
                                               only_unique=True)

# Saving results into csv file
with open('/Users/chrisbudnik/Desktop/Projects/youtube-research/datasets/channels/channel-list-online-business-v2.csv', 'w') as file:
    writer = csv.writer(file)
    header = ["channel_id", "channel_name", "uploads_playlist_id", "subscriber_count"]
    writer.writerow(header)

    for channel in tqdm(results, desc="Saving channel info ..."):
        channel_info = list(channel.info())
        writer.writerow(channel_info)

print(f"Successfuly saved {len(results)} channels.")

# Create a BigQuery Connection
connector = BigQueryConnector(dataset_id="youtube")

# Automated CSV insert allows for simple data upload


