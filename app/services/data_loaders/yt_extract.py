import datetime
import time

from pytube import YouTube
from googleapiclient.discovery import build
import json
import os
import requests
from youtube_transcript_api import YouTubeTranscriptApi
import re
import configparser
import pandas as pd

video_url = 'https://www.youtube.com/watch?v=GJTjDnMzYEk&list=PLfQhCXyy6psHjJXwDo4KQg8C_PbWVyWHp&index=16'


config = configparser.ConfigParser()
config.read('config.ini')

# YouTube API key
api_key = config['YOUTUBE']['API_KEY']



class YouTubeBase:
    def __init__(self, base_folder="../data"):
        self.base_folder = base_folder
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def save_to_json(self, data, filename):
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)


class YouTubeExtractor(YouTubeBase):

    def fetch_playlist_videos(self, playlist_url):
        playlist_id = self.extract_playlist_id(playlist_url)
        videos = []

        request = self.youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50
        )

        while request is not None:
            response = request.execute()
            videos += [item['snippet']['resourceId']['videoId'] for item in response.get('items', [])]
            request = self.youtube.playlistItems().list_next(request, response)

        return videos

    @staticmethod
    def extract_playlist_id(playlist_url):
        # Extract the playlist ID from the URL
        match = re.search(r'list=([0-9A-Za-z_-]+)', playlist_url)
        return match.group(1) if match else None

    def save_channel_info(self, channel_info, channel_id, filename='channel_info.csv'):
        data = {
            'channel_id': channel_id,
            'name': channel_info['Channel Name'],
            'total_subscribers': int(channel_info['Subscriber Count']),
            'total_view_count': int(channel_info['Total Views']),
            'description': channel_info['Description']
        }
        collection_name="channels"
        df = pd.DataFrame([data])
        df.to_csv(filename, mode='a', header=not os.path.exists(collection_name), index=False)
        # response = supabase.table(collection_name).upsert(data).execute()
        # return response

    def save_comments(self, video_id, comments, base_path, persons_filename='persons.csv', comments_filename='comments.csv'):
        person_data = {}
        comment_data = []

        for comment in comments:
            person_id = comment['author_channel_id']  # Using channel ID as a unique identifier

            # If person is not already in the dictionary, add them
            if person_id not in person_data:
                person_data[person_id] = {
                    'person_id': person_id,
                    'name': comment['author_name'],
                    'bio': f"Profile URL: {comment['author_channel_url']}, Image URL: {comment['author_profile_image_url']}",
                    'role': 'commenter'
                }

            comment_entry = {
                'comment_id': comment['comment_id'],
                'parent_id': comment.get('parent_id', None),  # Include parent comment ID
                'video_id': video_id,
                'author_id': person_id,
                'text': comment['text'],
                'comment_date': comment['published_at'],
                'like_count': comment['like_count']
            }
            comment_data.append(comment_entry)

        # Save person data to CSV
        if person_data:
            person_df = pd.DataFrame(person_data.values())
            persons_filename= os.path.join(base_path, persons_filename)
            person_df.to_csv(persons_filename, mode='a', header=not os.path.exists(persons_filename), index=False)

        # Save comment data to CSV
        if comment_data:
            comment_df = pd.DataFrame(comment_data)
            comments_filename = os.path.join(base_path, comments_filename)
            comment_df.to_csv(comments_filename, mode='a', header=not os.path.exists(comments_filename), index=False)

    def save_video_metadata(self, video_id, metadata, filename='video_metadata.csv'):
        data = {
            'video_id': video_id,
            'channel_id': metadata['ChannelId'],
            'title': metadata['Title'],
            'duration': metadata['Duration'],
            'upload_date': metadata['Upload Date'],
            'view_count': metadata['Views'],
            'description': metadata['Description']
        }
        df = pd.DataFrame([data])
        df.to_csv(filename, mode='a', header=not os.path.exists(filename), index=False)

    def save_audio_info(self, video_id, audio_file_path, filename='audio_info.csv'):
        data = {
            'video_id': [video_id],
            'audio_file_path': [audio_file_path]
        }
        df = pd.DataFrame(data)
        df.to_csv(filename, mode='a', header=not os.path.exists(filename), index=False)

    def save_transcript(self, video_id, transcript, filename='transcripts.csv'):
        # If the transcript is a list of strings, join them into a single string
        if isinstance(transcript, list):
            transcript = ' '.join(transcript)

        data = {
            'video_id': [video_id],
            'transcript': [transcript]
        }
        df = pd.DataFrame(data)
        df.to_csv(filename, mode='a', header=not os.path.exists(filename), index=False)

    def fetch_channel_info_from_video(self, video_url):
        try:
            video = YouTube(video_url)
            channel_id = video.channel_id
            request = self.youtube.channels().list(
                part="snippet,statistics",
                id=channel_id
            )
            response = request.execute()

            if 'items' in response and len(response['items']) > 0:
                channel_info = response['items'][0]
                data = {
                    'Channel Name': channel_info['snippet']['title'],
                    'Subscriber Count': channel_info['statistics']['subscriberCount'],
                    'Total Views': channel_info['statistics']['viewCount'],
                    'Total Videos': channel_info['statistics']['videoCount'],
                    'Description': channel_info['snippet']['description']
                }
                return data
            else:
                return "Channel information not found"
        except Exception as e:
            return str(e)

    def fetch_comments(self, video_id):
        try:
            comments = []
            next_page_token = None

            while True:
                response = self.youtube.commentThreads().list(
                    part="snippet,replies",
                    videoId=video_id,
                    maxResults=100,
                    pageToken=next_page_token,
                    textFormat="plainText"
                ).execute()

                for item in response.get("items", []):
                    top_level_comment = item["snippet"]["topLevelComment"]["snippet"]
                    comments.append(self.extract_comment(item['snippet']['topLevelComment'], parent_id=video_id))

                    # If there are replies, fetch them
                    if 'replies' in item:
                        for reply in item['replies']['comments']:
                            comments.append(
                                self.extract_comment(reply, parent_id=item['snippet']['topLevelComment']['id']))

                next_page_token = response.get("nextPageToken")
                if not next_page_token:
                    break

            return comments
        except Exception as e:
            return str(e)

    @staticmethod
    def extract_comment(comment_item, parent_id):
        snippet = comment_item['snippet']
        return {
            'comment_id': comment_item['id'],
            'parent_id': parent_id,  # This tracks the parent of the comment
            'text': snippet.get("textDisplay", ""),
            'author_name': snippet.get("authorDisplayName", ""),
            'author_channel_id': snippet["authorChannelId"].get("value", ""),
            'author_profile_image_url': snippet.get("authorProfileImageUrl", ""),
            'author_channel_url': snippet.get("authorChannelUrl", ""),
            'like_count': snippet.get("likeCount", 0),
            'published_at': snippet.get("publishedAt", "")
        }

    def fetch_video_metadata(self, video_url):
        try:
            video = YouTube(video_url)
            metadata = {
                'VideoID': video.video_id,
                'Title': video.title,
                'Uploader': video.author,
                'Upload Date': video.publish_date.strftime('%Y-%m-%d'),
                'Duration': video.length,
                'Views': video.views,
                'ChannelId': video.channel_id,
                'Description': video.description
            }
            return metadata
        except Exception as e:
            return str(e)

    def download_smallest_video_and_audio(self, video_url, folder='downloads'):
        try:
            video = YouTube(video_url)
            video_id = video.video_id

            if not os.path.exists(folder):
                os.makedirs(folder)

            audio_stream = video.streams.filter(only_audio=True, file_extension='mp4').order_by('abr').asc().first()

            if audio_stream:
                # Constructing the filename
                audio_filename = f'audio_{video_id}.mp3'
                download_path = os.path.join(folder, audio_filename)

                # Downloading the audio stream
                audio_stream.download(output_path=folder, filename=audio_filename)
                return f"Audio downloaded as {download_path}"
            else:
                return "No suitable audio stream found"
        except Exception as e:
            return str(e)

    def download_thumbnail(self, video_url, filename='thumbnail.jpg'):
        try:
            video = YouTube(video_url)
            thumbnail_url = video.thumbnail_url
            response = requests.get(thumbnail_url)

            if response.status_code == 200:
                with open(filename, 'wb') as file:
                    file.write(response.content)
                return f"Thumbnail saved as {filename}"
            else:
                return "Failed to download thumbnail"
        except Exception as e:
            return str(e)

    def fetch_transcript(self, video_id):
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_transcript(['en']).fetch()
            return transcript
        except Exception as e:
            return str(e)

    def save_transcript_as_text(self, video_id, transcript, folder='transcripts'):
        if not os.path.exists(folder):
            os.makedirs(folder)
        file_path = os.path.join(folder, f'{video_id}_transcript.txt')
        with open(file_path, 'w', encoding='utf-8') as file:
            for line in transcript:
                file.write(f"{line['text']}\n")
    def extract_youtube_data(self, video_url, api_key, base_folder):
        try:
            video_id = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', video_url).group(1)
        except AttributeError:
            print(f"Invalid YouTube URL: {video_url}")
            return

        folder_path = os.path.join(base_folder, video_id)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        try:
            channel_info = self.fetch_channel_info_from_video(video_url)
            if channel_info:
                channel_id = YouTube(video_url).channel_id
                self.save_channel_info(channel_info, channel_id, os.path.join(folder_path, 'channel_info.csv'))

            # Fetch and save video metadata
            metadata = self.fetch_video_metadata(video_url)
            metadata['folder_path'] = folder_path
            if metadata:
                self.save_video_metadata(video_id, metadata, os.path.join(folder_path, 'video_metadata.csv'))

            # Fetch and save comments
            comments = self.fetch_comments(video_id)
            if comments:
                self.save_comments(video_id, comments, folder_path)

            # Download audio and save its info
            audio_download_result = self.download_smallest_video_and_audio(video_url, folder_path)
            # Implement saving audio info if required

            # Download thumbnail and save its info
            thumbnail_download_result = self.download_thumbnail(video_url, os.path.join(folder_path, 'thumbnail.jpg'))
            # Implement saving thumbnail info if required

            # Fetch and save transcript
            try:
                transcript = self.fetch_transcript(video_id)
                self.save_transcript_as_text(video_id,transcript,folder_path)
            except Exception as e:
                pass
        except Exception as e:
            print(f"{video_id} An error occurred: {e} ")
            return None

        return metadata

    def process_video(self, video_url, folder=None):
        start_time = time.time()

        # folder = os.path.join(self.base_folder, folder)
        video_metadata = self.extract_youtube_data(video_url, self.api_key, folder)
        processing_time = time.time() - start_time

        if video_metadata:
            return {
                'video_id': video_metadata['VideoID'],
                'video_title': video_metadata['Title'],
                'processing_time': processing_time
            }
        else:
            return None

    def process_playlist(self, playlist_url):
        video_ids = self.fetch_playlist_videos(playlist_url)
        total_videos = len(video_ids)
        processed_videos_count = 0
        total_duration = datetime.timedelta()
        processed_videos_info = []

        for video_id in video_ids:
            video_url = f'https://www.youtube.com/watch?v={video_id}'
            result = self.process_video(video_url)

            if result:
                processed_videos_count += 1
                total_duration += datetime.timedelta(seconds=result['processing_time'])
                processed_videos_info.append(result)

                # Calculate expected time to finish
                average_time_per_video = total_duration / processed_videos_count
                remaining_videos = total_videos - processed_videos_count
                expected_time_to_finish = average_time_per_video * remaining_videos

                playlist_response = {
                    'last_processed_video_id': result['video_id'],
                    'total_videos': total_videos,
                    'processed_videos_count': processed_videos_count,
                    'total_duration': str(total_duration),
                    'expected_time_to_finish': str(expected_time_to_finish)
                }

                # Returning or yielding the JSON for each processed video
                yield json.dumps(playlist_response)

            else:
                # Handle error or continue processing the next video
                continue

if __name__ == '__main__':
    base_folder =  '../../../data'
    extractor = YouTubeExtractor(api_key,base_folder)
    # extractor.extract_youtube_data(video_url, api_key, 'downloaded_data')
    playlist_url = 'https://www.youtube.com/watch?v=GVRtzbxbunY&list=PLX_rhFRRlAG41ubK41B_OXEV3LEjLFuRU'
    video_ids = extractor.fetch_playlist_videos(playlist_url)

    for video_id in video_ids:
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        extractor.extract_youtube_data(video_url, api_key)