import yt_dlp
from translators import LocalWhisperModel

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

class ProcessAudio:
    def __init__(self, file: str):
        self.file = file

    def transcribe_with_local_whisper_model(self, model : str="turbo"):
        transcription = LocalWhisperModel(model, file=self.file)
        return transcription



