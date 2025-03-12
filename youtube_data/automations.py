from .client import YouTube
from .models import Channel, Video, VideoTranscript
from .utils import create_chunks


def channel_ids_to_video_details(
    youtube: YouTube,
    channel_ids: list[str],
    videos_per_channel: int = 50,
    videos_per_request: int = 50,
) -> list[Video]:
    """
    Takes a list of channel ids and returns a list of video details.
    This process involves getting the uploads playlist id for each channel 
    and then getting the video details for each video in the uploads playlist.
    Last step is to return a list of video details from all the channels.

    Args:
        youtube: YouTube: The YouTube object.
        channel_ids: list[str]: The list of channel ids.
        videos_per_channel: int: The number of videos to get per channel.
        videos_per_request: int: The number of videos to get per request.
    
    Returns:
        list[Video]: The list of video details.
    """

    channels = youtube.get_channel_details(channel_ids)
    channel_playlists = [channel.uploads_playlist_id for channel in channels]
    
    channel_video_ids = []
    for playlist_id in channel_playlists:
        playlist_items = youtube.get_playlist_items(
            playlist_id, max_results=videos_per_channel
            )
        channel_video_ids.extend([item.video_id for item in playlist_items])

    videos_chunked = create_chunks(channel_video_ids, videos_per_request)
    videos_data = []
    for chunk in videos_chunked:
        videos_data += youtube.get_video_details(chunk)

    return videos_data


def video_ids_to_video_details(
    youtube: YouTube,
    video_ids: list[str],
    videos_per_channel: int = 50,
    videos_per_request: int = 50,
) -> list[Video]:
    """
    Takes a list of video ids and returns a list of video details.
    Analagous to channel_ids_to_video_details but for video ids.
    Channel ids are extracted from the video ids, then process is the same.

    Args:
        youtube: YouTube: The YouTube object.
        video_ids: list[str]: The list of video ids.
        videos_per_channel: int: The number of videos to get per channel.
        videos_per_request: int: The number of videos to get per request.

    Returns:
        list[Video]: The list of video
    """

    videos_as_channels = youtube.get_video_details(video_ids)
    channel_ids = [video.channel_id for video in videos_as_channels]

    return channel_ids_to_video_details(
        youtube, channel_ids, videos_per_channel, videos_per_request
    )


def search_queries_to_channels(
    youtube: YouTube,
    queries: list[str],
    ) -> list[Channel]:
    pass


def video_ids_to_transcripts(
    youtube: YouTube,
    video_ids: list[str],
    ) -> list[VideoTranscript]:

    transcripts = []
    for id in video_ids:
        transcript = youtube.get_video_transcript(id)
        transcripts.append(transcript)

    return transcripts


