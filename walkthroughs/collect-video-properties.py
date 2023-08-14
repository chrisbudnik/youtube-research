# Tutorial Outline
# 1. Retrive channel ids from csv file (channel-list-custom.csv)
# 2. Collect video properties with `VideoDataCollector` 
# 3. Save results into csv file (get data from latest 25 videos)
# 4. Export data to bigquery table - videos_base

import sys
sys.path.append('/Users/chrisbudnik/Desktop/Projects/youtube-research')

import csv
from models.data_collectors import VideoDataCollector
from databases.bigquery_connector import BigQueryConnector


# Save channel ids in list format from csv file
channel_ids = []
with open('/Users/chrisbudnik/Desktop/Projects/youtube-research/datasets/channels/channel-list-custom.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        channel_ids.append(row['channel_id'])

# Create an instance of VideoDataCollector
collector = VideoDataCollector(channel_ids=channel_ids)

# Collect video data from channel ids
data_from_channels = collector.collect_data_from_channels(max_videos=25)

with open('/Users/chrisbudnik/Desktop/Projects/youtube-research/datasets/project-samples/video-properties.csv', 'w') as file:
    writer = csv.writer(file)
    header = ["video_id", "video_name", "channel_id", "channel_name",
              "category_id", "published_at", "video_length", "type",
              "license", "made_for_kids", "user_tags", "description",
              "transcript"]
    
    writer.writerow(header)

    for video in data_from_channels:
        properties = list(video.values())
        writer.writerow(properties)

print(f"Successfuly saved data from {len(data_from_channels)} video.")


rows_to_insert = [tuple(item.values()) for item in data_from_channels]

# Create a BigQuery Connection
connector = BigQueryConnector(dataset_id="youtube")

# Automated insert allows for simple data upload
connector.automated_insert(table_name="video_base", rows=rows_to_insert)

