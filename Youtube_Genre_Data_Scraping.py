# -*- coding: utf-8 -*-
"""Untitled7.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1N8B07_n_MfUCcXGpGYDs1OssoajnEP1N
"""

pip install google-api-python-client pandas youtube-transcript-api

from googleapiclient.discovery import build
import pandas as pd

api_key = 'AIzaSyDq2CZFXmigroLycxzXxJXJoChqI3Tkgt8'
youtube = build('youtube', 'v3', developerKey= api_key)

def fetch_videos_by_genre(genre, max_results=500):
    videos = []
    next_page_token = None

    while len(videos) < max_results:
        response = youtube.search().list(
            q=genre,
            type='video',
            part='id,snippet',
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        for item in response['items']:
            video_id = item['id']['videoId']
            videos.append(video_id)
            if len(videos) >= max_results:
                break  # Stop if we reach the desired number of results

        # Get the next page token
        next_page_token = response.get('nextPageToken')
        if not next_page_token:  # Break if no more pages
            break

    return videos

def fetch_video_details(video_ids):
    video_details = []
    for i in range(0, len(video_ids), 50):  # Process in batches of 50
        response = youtube.videos().list(
            part='snippet,contentDetails,statistics,topicDetails,recordingDetails',
            id=','.join(video_ids[i:i+50])
        ).execute()

        for video in response['items']:
            video_details.append({
                'Video URL': f"https://www.youtube.com/watch?v={video['id']}",
                'Title': video['snippet']['title'],
                'Description': video['snippet']['description'],
                'Channel Title': video['snippet']['channelTitle'],
                'Keyword Tags': video['snippet'].get('tags', []),
                'Category': video['snippet']['categoryId'],
                'Published At': video['snippet']['publishedAt'],
                'Duration': video['contentDetails']['duration'][2:],
                'View Count': video['statistics'].get('viewCount', 0),
                'Comment Count': video['statistics'].get('commentCount', 0),
                'Topic Details': video.get('topicDetails', {}).get('topicCategories', []),
                'Location of Recording': video.get('recordingDetails', {}).get('location'),
                'Captions Available': False,  # Initialize to False; update later
                'Caption Text': None  # Initialize as None; update later
            })
    return video_details

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, VideoUnavailable

def fetch_captions(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([item['text'] for item in transcript])
    except TranscriptsDisabled:
        print(f"Transcripts are disabled for video ID: {video_id}")
        return None
    except VideoUnavailable:
        print(f"Video unavailable for ID: {video_id}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred for video ID {video_id}: {e}")
        return None


youtube_video_details = fetch_video_details(fetch_videos_by_genre('Anime'))

for i in range(len(youtube_video_details)):
    video_id = youtube_video_details[i]['Video URL'].split('=')[-1]
    captions = fetch_captions(video_id)

for video in youtube_video_details:
    captions = fetch_captions(video['Video URL'].split('=')[-1])
    video['Captions Available'] = bool(captions)
    if captions:
        # Replace newline characters with spaces and wrap in double quotes
        cleaned_caption = captions.replace('\n', '').replace('"', '').replace(',', '').replace("'", "").replace('\r', ' ')  # Escape existing double quotes
        video['Caption Text'] = cleaned_caption
    else:
        video['Caption Text'] = None

import pandas as pd
def save_to_csv(data, filename='anime.csv'):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

save_to_csv(youtube_video_details)