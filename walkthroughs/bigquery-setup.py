import sys
sys.path.append("/Users/chrisbudnik/Desktop/Projects/youtube-research")

from databases.bigquery_connector import BigQueryConnector

# Connect bigquery to dataset (where youtube data will be stored)
conn = BigQueryConnector(dataset_id="main")

# Create project tables
conn.automated_create_tables()