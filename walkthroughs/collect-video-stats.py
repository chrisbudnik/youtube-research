# Tutorial Outline
# 1. import video list from Bigquery (video_base table)
# 2. Collect video stats with `VideoDataCollector` 
# 3. Save results into csv file (for back-up)
# 4. Export data to bigquery table - videos_stats

import sys
sys.path.append('/Users/chrisbudnik/Desktop/Projects/youtube-research')

import csv
from models.data_collectors import VideoDataCollector
from databases.bigquery_connector import BigQueryConnector
from databases.bigquery_connector import BigQueryTableNames


# Instance of BigQuery Connector, working with youtube dataset
connector = BigQueryConnector(dataset_id="youtube")

# Using automated_query method to fetch video_ids from video_base table
video_ids = connector.automated_query(BigQueryTableNames.VIDEO_BASE, columns=["video_id"])

# Passing video ids from video_base table to collector class
collector = VideoDataCollector(video_ids=video_ids)

# Get current data on video stats in dict format
data_from_videos = collector.collect_data_from_videos()
print("Completed collecting video stats")

# Saving data into csv as back-up
with open('/Users/chrisbudnik/Desktop/Projects/youtube-research/datasets/project-samples/video-stats-2023-08-15.csv', 'w') as file:
    writer = csv.writer(file)
    header = ["date", "video_id", "views", "likes", "comments"]
    writer.writerow(header)

    for video in data_from_videos:
        properties = list(video.values())
        writer.writerow(properties)

print(f"Successfuly saved data from {len(data_from_videos)} videos into csv.")

# Export results to BigQuery video_stats table
connector.automated_insert(BigQueryTableNames.VIDEO_STATS, data_from_videos)
print("Data insert is compleated.")


