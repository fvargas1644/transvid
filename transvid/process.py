import yt_dlp
from utils import format_timestamp, FileManager, convert_to_mkv, create_video_with_audio, format_timestamp_for_srt_files 
from openai_models import LocalWhisperModel
from moviepy import VideoFileClip
from translators import TranslateAudio


def create_srt_file_with_local_whisper_model(file: str, srt_file : str, model : str = "turbo"):

    whisper = LocalWhisperModel(file=file, model=model)
    transcription = whisper.transcribe()

    with open(srt_file, 'w', encoding='utf-8') as str_file_name:
        str_file_name.write("Hola")
        for segment in transcription['segments']:
            
            start_time = format_timestamp_for_srt_files(segment['start'])
            end_time = format_timestamp_for_srt_files(segment['end'])
            text = segment['text'].lstrip() 
            segment_id = segment['id'] + 1

            srt_entry = f"{segment_id}\n{start_time} --> {end_time}\n{text}\n\n"
            str_file_name.write(srt_entry)


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
    def __init__(self, video_path : str):
        self.video_path = FileManager().check_file(file=video_path)

    def create_translated_video(
            self, 
            target_lang : str='es', 
            source_lang : str =None,
            openai_api_key: str = None,
            voice_config : dict  = None
        ):

        if voice_config is None:
            voice_config = {
                "model": "tts-1",
                "voice": "onyx",
                "instructions": "",
                "speed": 1.0
            }


        file_manager = FileManager()
        file_manager.create_structure()

        video_main_mkv  = convert_to_mkv(self.video_path, f'{file_manager.videos_folder}/video_main.mkv')
        audio_main_wav = VideoFileClip(video_main_mkv).audio 

        audio_main_wav.write_audiofile(f'{file_manager.audios_folder}/audio_main.wav')

        translate_audio = TranslateAudio(
            file=f'{file_manager.audios_folder}/audio_main.wav', 
            target_lang=target_lang, 
            source_lang=source_lang
        )

        transcription = translate_audio.transcribe_with_local_whisper_model(model="base")

        # Remember to use deepl
        translated_transcript = translate_audio.translate(text=transcription["text"])


        audios = translate_audio.convert_text_to_audio_with_openai(
            text=translated_transcript, 
            folder=file_manager.audios_folder,
            api_key=openai_api_key
        )

        i=0
        for audio in audios:
            status = create_video_with_audio(
                output_video=f'{file_manager.videos_folder}/{i}.mkv', 
                audio_file=audio
            )

            if not status:
                # Combine the audio files into a single audio file and return it
                return