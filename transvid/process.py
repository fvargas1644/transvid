import yt_dlp
from utils import FileManager, convert_to_mkv, create_video_with_audio, format_timestamp_for_srt_files, embed_subtitles
from openai_models import LocalWhisperModel
from moviepy import VideoFileClip, concatenate_videoclips
from translators import TranslateAudio


def create_srt_file_with_local_whisper_model(file: str, srt_file : str, model : str = "turbo"):

    FileManager().check_path(file)

    whisper = LocalWhisperModel(file=file, model=model)
    transcription = whisper.transcribe()

    with open(srt_file, 'w', encoding='utf-8') as str_file_name:
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

class Video:
    def __init__(self, video_path : str):
        self.video_path = FileManager().check_path(path=video_path)

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

        video_main_mkv  = convert_to_mkv(self.video_path, f'{file_manager.videos_folder}/main_video.mkv')
        audio_main_wav = VideoFileClip(video_main_mkv).audio 

        audio_main_wav.write_audiofile(f'{file_manager.audios_folder}/main_audio.wav')

        translate_audio = TranslateAudio(
            file=f'{file_manager.audios_folder}/main_audio.wav', 
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

        subtitle_videos = []
        basic_videos = []

        for audio in audios:
            srt_file = f'{file_manager.transcriptions_folder}/{i}.srt'
            basic_video = f'{file_manager.videos_folder}/basic_video{i}.mkv'
            subtitle_video = f'{file_manager.videos_folder}/subtitle_video{i}.mkv'


            create_srt_file_with_local_whisper_model(
                file=audio, 
                srt_file=srt_file
            )

            status = create_video_with_audio(
                output_video=basic_video, 
                audio_file=audio
            )

            embed_subtitles(
                input_video=basic_video, 
                subtitles_file=srt_file, 
                output_video=subtitle_video
            )

            if not status:
                # Combine the audio files into a single audio file and return it
                return

            subtitle_videos.append(subtitle_video)
            basic_videos.append(basic_video)

            i +=1
        
        subtitle_main_video = concatenate_videoclips(subtitle_videos)
        subtitle_main_video.write_videofile("video_final.mkv", codec="libx264", audio_codec="aac")