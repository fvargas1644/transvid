import yt_dlp
from openai_models import LocalWhisperModel
from translators import TextTranslators
import asyncio

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
        return transcription.transcribe()
    
    def translate(self, text: str, auth_key: str = None, target_lang :str='es', source_lang :str=None, translator : str="googletrans"):
        translation = TextTranslators(text=text, target_lang=target_lang, source_lang=source_lang)
        translation = translation.translate(auth_key=auth_key, translator=translator)
        return translation





