# Youtube Research

> :warning: **Heads Up!** :warning:
>
> Hey there! I'm shuffling things around a bit. 
>
> - Stuff related to the **YouTube API v3** and pulling data from YouTube? It's now over at [`youtube-data`](https://github.com/your-username/youtube-data). You'll find some cool examples there too.
> - All the **custom database connectors**? They've found a new home at [`youtube-databases`](https://github.com/your-username/youtube-databases).
>
> Thanks for sticking around during the shuffle! Check out the new repos for the goodies you're after.


Welcome to the Youtube-Research repository. Dive into an efficient suite designed for extracting and analyzing data from YouTube using the YT API v3. Built with Python, this repository provides comprehensive modules to get the most out of YouTube data.


## 📌 Features:
- **`Video`**: Extract both static properties and dynamic stats.
- **`Playlist`**: Fetch video IDs from any given playlist.
- **`Channel`**: Retrieve all video IDs associated with a channel.
- **`YoutubeSearch`**: A dedicated class to find channels or inspect video IDs.
- **Data Collectors (`VideoDataCollector`)**: A seamless interface to fetch video data based on video or channel IDs.
- **BigQuery Integration** - custom connector for importing/exporting data from BigQuery

## 📁 Directory Structure:
### 1. `tutorials`
- Provides instructive code samples for various functionalities including:
  - Channel discovery.
  - Finding channel IDs.
  - Extracting video properties.
  - Retrieving video stats.
  - BigQuery setup and more.

### 2. `youtube`
- This directory houses core functionality and classes associated with YouTube data extraction and manipulation:
  - Video, Playlist, and Channel classes for various data extraction tasks.
  - YoutubeSearch class for enhanced search functionality.
  - VideoDataCollector interface for a cohesive data collection experience.

### 3. `databases`
- Contains the `BigQueryConnector` class, a custom connector for Google BigQuery. Features include:
  - Automated setup: Instantly create your project tables.
  - Simplified data operations: Automated inserts, querying, and more for an enhanced experience with BigQuery.

### 4. `datasets`
- Repository for data files critical to the toolset:
  - Search-term lists for channel exploration.
  - A curated list of channels for data collection.
  - Project setup files.

## 🔧 Requirements:
- Python
- YT API v3 credentials
- *more - description in progress*

## 🚀 Getting Started:
1. Clone the repository.
2. Set up your YT API v3 and BigQuery credentials in `config.py` file. Then change its name to `configuration.py`
3. Navigate to the `tutorials` directory to understand the working and integration of various modules.
4. Explore the `youtube`, and `databases` directories for more specialized operations.
5. In `datasets` data is located including: search terms, 

## Contributions:
Feel free to raise issues, suggest enhancements, or make pull requests. Your feedback is invaluable!

Thank you for choosing the Youtube Data Toolset. Let's make the most out of YouTube data together!