from enum import Enum
from typing import Union, List, Dict

from google.api_core.exceptions import NotFound
from google.cloud import bigquery
from tqdm import tqdm

from configuration import Config
from .bigquery_schemas import Schema


class BigQueryTableNames(Enum):
    VIDEO_BASE = "video_base"
    VIDEO_STATS = "video_stats"
    VIDEO_TEXT = "video_text"
    CHANNELS = "channels"


class BigQueryConnector:
    """
    Class to interact with BigQuery, providing utilities to create tables,
    insert data, and retrieve data from the defined schemas and table names.
    """
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
        SCHEMAS = [tbl.value for tbl in list(Schema)]
        TABLE_NAMES = [tbl.value for tbl in list(BigQueryTableNames)]

        for table_id, schema in tqdm(zip(TABLE_NAMES, SCHEMAS), desc="Creating main project tables..."):
            table_ref = self.client.dataset(self.dataset_id).table(table_id)

            try:
                self.client.get_table(table_ref)
                raise NotImplementedError(f"'{table_id}' table already exists, error is raised to prevent data loss. In dataset: '{self.dataset_id}' should be no {self.TABLE_NAMES} tables")
            except NotFound:
                pass

            table = bigquery.Table(table_ref, schema=schema)
            table = self.client.create_table(table)
        
        print(f"Succesfully created youtube-research project tables: {TABLE_NAMES}")

    def automated_insert(self, table_name: BigQueryTableNames, data: list[dict]) -> None:
        """
        Insert rows into the specified table.
        """
        table_ref = self.client.dataset(self.dataset_id).table(table_name.value)
        table = self.client.get_table(table_ref)

        rows_to_insert = [tuple(item.values()) for item in data]
        errors = self.client.insert_rows(table, rows_to_insert)

        if errors:
            raise Exception(f"Encountered errors while inserting rows into {table_name}: {errors}")
        
    def automated_query(self, table_name: BigQueryTableNames, columns: List[str]) -> Union[List[str], Dict[str, List]]:
        """
        Automated query allows simplified data download from main project tables. 
        """
        sql = f"""SELECT {'.'.join(columns)} FROM `youtube-research-2023.{self.dataset_id}.{table_name.value}` LIMIT 10""",
        return self.query(sql)

    
    def query(self, sql: str) -> Union[List[str], Dict[str, List]]:
        """
        Query BigQuery table based on provided sql. If only one column is selected, list of values is returned, 
        otherwise dict is returned with each key as column name and its value as list of column's values. 
        """
        query_job = self.client.query(sql)
        results = query_job.result()

        if results.schema and len(results.schema) == 1:
            return [row[0] for row in results]
        
        else:
            output_dict = {}
            for field in results.schema:
                output_dict[field.name] = []
            
            for row in results:
                for field in results.schema:
                    output_dict[field.name].append(row[field.name])
            
        return output_dict


