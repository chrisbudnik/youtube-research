from google.cloud import bigquery
from google.api_core import exceptions
from typing import Literal
from config import Config
from bigquery_schemas import Schema
from tqdm import tqdm


# TO-DO: methods: insert, get data
# TO-DO: add doc strings for existing tables
class BigQueryConnector:
    SCHEMAS = [Schema.VIDEO_BASE, Schema.VIDEO_STATS, Schema.VIDEO_TEXT, Schema.CHANNELS]
    TABLE_NAMES = ["video_base", "video_stats", "video_text", "channel"]
    
    def __init__(self, dataset_id):
        self.client = bigquery.Client.from_service_account_json(Config.BQ_SERVICE_ACCOUNT_KEYS_PATH)
        self.dataset_id = dataset_id

    def automated_create_tables(self) -> None:
        for table_id, schema in tqdm(zip(self.TABLE_NAMES, self.SCHEMAS), desc=f"Creating {table_id} table"):
            table_ref = self.client.dataset(self.dataset_id).table(table_id)

            # if table exists, return error
            if self.client.get_table(table_ref):
                raise NotImplementedError(f"{table_id} already exists, error is raised to prevent data loss. In {self.dataset_id} should be no {self.TABLE_NAMES} tables")

            table = bigquery.Table(table_ref, schema=schema)
            table = self.client.create_table(table) 