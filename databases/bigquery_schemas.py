from google.cloud import bigquery


# TO-DO: prepare schema for video_text table
class Schema:
    """
    Schema class serves as a storage for bigquery schemas. 
    Names relate to corresonding main project tables. 
    The purpose of this class is to simplify the set-up process for 
    youtube data analysis
    """
    VIDEO_BASE = [
        bigquery.SchemaField("video_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("video_title", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("channel_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("channel_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("category_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("published_at", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("video_length", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("type", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("license", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("made_for_kids", "BOOL", mode="REQUIRED"),
        bigquery.SchemaField("user_tags", "STRING", mode="REPEATED"),
        bigquery.SchemaField("description", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("transcript", "STRING", mode="REQUIRED"),
    ] 
        
    VIDEO_STATS = [
        bigquery.SchemaField("date", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("video_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("views", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("likes", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("comments", "FLOAT", mode="REQUIRED"),
    ] 
    
    VIDEO_TEXT = [
        bigquery.SchemaField("video_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("transcript", "STRING", mode="REQUIRED"),
        
    ]
    
    CHANNELS = [
        bigquery.SchemaField("channel_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("channel_name", "STRING", mode="REQUIRED"),
    ]
