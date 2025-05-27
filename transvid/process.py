import yt_dlp
from utils import format_timestamp, FileManager, convert_to_mkv
from openai_models import LocalWhisperModel


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
    
    def create_srt_file_with_local_whisper_model(self, model : str="turbo", folder : str = None):

        path_components = FileManager().path_components(self.audio_file)

        transcription = LocalWhisperModel(file=self.audio_file, model=model).transcribe()

        file = FileManager().check_path(file=f"{path_components[1]}.srt", folder=folder) if folder != None else f"{path_components[1]}.srt"

        with open(file, 'w', encoding='utf-8') as file_srt:
            for segment in transcription['segments']:
                start_time = format_timestamp(segment['start'])
                end_time = format_timestamp(segment['end'])

                text = segment['text'].lstrip() 
                segment_id = segment['id'] + 1

                srt_entry = f"{segment_id}\n{start_time} --> {end_time}\n{text}\n\n"
                file_srt.write(srt_entry)

class Video:
    def __init__(self, video_path : str = None):
        self.video_path = FileManager().check_file(file=video_path)

    def create_translated_video(self):
        file_manager = FileManager()
        file_manager.create_structure()

        video_main_mkv  = convert_to_mkv(self.video_path, f'{file_manager.main_folder}/main.mkv')


