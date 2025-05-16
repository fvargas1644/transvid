import yt_dlp
from utils import format_timestamp


class DownloadYoutubeVideo:
    def __init__(
        self, 
        url : str, 
        quality: str="bestvideo+bestaudio/best", 
        format_output: str="mkv", 
        output_name : str = "video_youtube"
    ):
        self.url = url
        self.download_options = {
            "format": quality,
            "merge_output_format": format_output,
            "outtmpl": output_name
        }

    def download_video(self):
        with yt_dlp.YoutubeDL(self.download_options) as video:
            video.download([self.url])

class Transcribe:
    def __init__(self, audio_file=str):
        self.audio_file = audio_file
    
    def create_srt_file(self, segments, filename_str : str):

        with open(filename_str, 'w', encoding='utf-8') as file_str:
            for segment in segments:
                start_time = format_timestamp(segment['start'])
                end_time = format_timestamp(segment['end'])

                text = segment['text'].lstrip() 
                segment_id = segment['id'] + 1

                srt_entry = f"{segment_id}\n{start_time} --> {end_time}\n{text}\n\n"
                file_str.write(srt_entry)

