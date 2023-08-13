from enum import Enum
from typing import Literal

from google.api_core.exceptions import NotFound
from google.cloud import bigquery
from tqdm import tqdm

from configuration import Config
from .bigquery_schemas import Schema


class TableNames(Enum):
    VIDEO_BASE = "video_base"
    VIDEO_STATS = "video_stats"
    VIDEO_TEXT = "video_text"
    CHANNELS = "channels"


class BigQueryConnector:
    """
    Class to interact with BigQuery, providing utilities to create tables,
    insert data, and retrieve data from the defined schemas and table names.
    """

    SCHEMAS = [tbl.value for tbl in list(Schema)]
    TABLE_NAMES = [tbl.value for tbl in list(TableNames)]

    def __init__(self, dataset_id):
        """
        Initialize the BigQuery client with the specified dataset ID.
        """
        self.client = bigquery.Client.from_service_account_json(Config.BQ_SERVICE_ACCOUNT_KEYS_PATH)
        self.dataset_id = dataset_id

    def automated_create_tables(self) -> None:
        """
        Automatically create tables with pre-defined schemas if they don't already exist.
        In other case, error is raised to prevent data loss.
        """
        for table_id, schema in tqdm(zip(self.TABLE_NAMES, self.SCHEMAS), desc="Creating main project tables..."):
            table_ref = self.client.dataset(self.dataset_id).table(table_id)

            try:
                self.client.get_table(table_ref)
                raise NotImplementedError(f"'{table_id}' table already exists, error is raised to prevent data loss. In dataset: '{self.dataset_id}' should be no {self.TABLE_NAMES} tables")
            except NotFound:
                pass

            table = bigquery.Table(table_ref, schema=schema)
            table = self.client.create_table(table)
        
        print(f"Succesfully created youtube-research tables: {self.TABLE_NAMES}")

    def automated_insert(self, table_name: str, rows: list) -> None:
        """
        Insert rows into the specified table.
        """
        table_ref = self.client.dataset(self.dataset_id).table(table_name)
        table = self.client.get_table(table_ref)
        errors = self.client.insert_rows(table, rows)

        if errors:
            raise Exception(f"Encountered errors while inserting rows into {table_name}: {errors}")

