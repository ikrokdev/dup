import json, grpc
import os

from app.services.data_loaders.proto import data_loaders_pb2_grpc, data_loaders_pb2
from app.services.data_loaders.yt_extract import YouTubeExtractor
from app.analysers.WhisperXTranscriber import WhisperXTranscriber

class YTProcessorService(data_loaders_pb2_grpc.YouTubeProcessorServicer):
    def __init__(self):
        self.base_folder = os.path.abspath("../data")
        self.processor = YouTubeExtractor(self.base_folder)

    def ProcessVideo(self, request, context):
        folder = "vkey@comp-A"
        folder = os.path.join(self.base_folder, folder)
        video_data = self.processor.process_video(request.file_url,folder)
        transcriber = WhisperXTranscriber()
        transcriber.process_directory(os.path.join(folder,video_data['video_id']))

        if video_data:
            return data_loaders_pb2.ProcessVideoResponse(
                video_id=video_data['video_id'],
                video_title=video_data['video_title'],
                processing_time=str(video_data['processing_time'])
            )
        else:
            # Handle the error scenario
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Video processing failed')
            return data_loaders_pb2_grpc.ProcessVideoResponse()

    def ProcessVideoPlaylist(self, request, context):
        for stats_json in self.processor.process_playlist(request.playlist_url):
            stats = json.loads(stats_json)
            yield data_loaders_pb2.ProcessVideoPlaylistResponse(
                last_processed_video_id=stats['last_processed_video_id'],
                total_videos=stats['total_videos'],
                processed_videos_count=stats['processed_videos_count'],
                total_duration=stats['total_duration'],
                expected_time_to_finish=stats['expected_time_to_finish']
            )
