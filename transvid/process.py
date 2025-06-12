import yt_dlp
from utils import FileManager, change_file_format, create_video_with_audio, format_timestamp_for_srt_files, embed_subtitles, merge_audios, validate_media
from openai_models import LocalWhisperModel
from moviepy import VideoFileClip, concatenate_videoclips
from translators import TranslateAudio
from pathlib import Path
from errors import InvalidFileType
from uuid import uuid4


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

class GenerateTranslation:
    def __init__(
            self, 
            file : str,
            target_lang : str, 
            source_lang : str =None,
            openai_api_key: str = None,
        ):
        
        self.file = FileManager().check_path(path=file)
        self.target_lang = target_lang
        self.source_lang = source_lang
        self.openai_api_key = openai_api_key


    def __validate_dictionaries(
            initial_voice_settings : dict = None, 
            initial_transcription_settings: dict = None,
            initial_translate_settings : dict = None,
        ):

        if initial_voice_settings is None:
            voice_settings = {
                "model": "tts-1",
                "voice": "onyx",
                "instructions": "",
                "speed": 1.0
            }
        else:
            voice_settings = {
                "model": initial_voice_settings.get("model", "tts-1"),
                "voice": initial_voice_settings.get("voice", "onyx"),
                "instructions": initial_voice_settings.get("instructions", ""),
                "speed": initial_voice_settings.get("speed", 1.0),
            }

        if initial_transcription_settings is None:
            transcription_settings = {
                "model": "turbo"
            }

        else:
            transcription_settings  = {
                "model": initial_transcription_settings.get("model", "turbo")
            }

        if initial_translate_settings is None:
            translate_settings = {
                "translator": "gooogletrans",
                "auth_key": None
            }

        else:
            translate_settings  = {
                "translator": initial_translate_settings.get("translator", "googletrans"),
                "auth_key": initial_translate_settings.get("auth_key", None)
            }

        return voice_settings, transcription_settings, translate_settings
    
    def __extract_audio(
            self, 
            voice_settings : dict, 
            transcription_settings : dict, 
            translate_settings : dict
        ):
        
        voice_settings, transcription_settings, translate_settings = self.__validate_dictionaries(
            voice_settings, 
            transcription_settings,
            translate_settings
        )

        file_manager = FileManager()
        file_manager.create_structure()

        target_file = validate_media(self.file)

        if  target_file== "video":
            video_main_mkv  = change_file_format(self.file, f'{file_manager.videos_folder}/main_video.mkv')
            audio_main_wav = VideoFileClip(video_main_mkv).audio 
            audio_main_wav.write_audiofile(f'{file_manager.audios_folder}/main_audio.wav')
        
        else:
            change_file_format(input_file=self.file, output_file=f'{file_manager.audios_folder}/main_audio.wav')

        translate_audio = TranslateAudio(
            file=f'{file_manager.audios_folder}/main_audio.wav', 
            target_lang=self.target_lang, 
            source_lang=self.source_lang
        )

        transcription = translate_audio.transcribe_with_local_whisper_model(
            model=transcription_settings["model"]
        )

        translated_transcript = translate_audio.translate(
            text=transcription["text"],
            auth_key=translate_settings["auth_key"],
            translator=translate_settings["translator"]
        )


        audios = translate_audio.convert_text_to_audio_with_openai(
            text=translated_transcript, 
            folder=file_manager.audios_folder,
            api_key=self.openai_api_key,
            model=voice_settings["model"],
            voice=voice_settings["voice"],
            instructions=voice_settings["instructions"],
            speed=voice_settings["speed"]
        )

        return audios, transcription_settings, file_manager


    def create_video(
            self, 
            ouput_video : str,
            voice_settings : dict  = None,
            transcription_settings : dict = None,
            translate_settings : dict = None,
        ):  

        if Path(ouput_video).exists(): raise FileExistsError(f'The video file {ouput_video} already exists')

        # Validate whether the output file is a video
        if validate_media(file=ouput_video) != "video": raise InvalidFileType(f"The file '{ouput_video}' is not a valid video file.")

        audios, transcription_settings, file_manager = self.__extract_audio(voice_settings, transcription_settings, translate_settings)        

        i=0

        subtitle_videos = []

        for audio in audios:
            srt_file = f'{file_manager.transcriptions_folder}/{i}.srt'
            basic_video = f'{file_manager.videos_folder}/basic_video{i}.mkv'
            subtitle_video = f'{file_manager.videos_folder}/subtitle_video{i}.mkv'


            create_srt_file_with_local_whisper_model(
                file=audio, 
                srt_file=srt_file,
                model=transcription_settings["model"]
            )

            status_basic_video = create_video_with_audio(
                output_video=basic_video, 
                audio_file=audio
            )

            status_subtitle_video = embed_subtitles(
                input_video=basic_video, 
                subtitles_file=srt_file, 
                output_video=subtitle_video
            )

            if not status_basic_video or not status_subtitle_video:
                merge_audios(audio_files=audios, output=f'transvid_audio_{uuid4().hex}.wav')
                print("The video could not be created. It was not possible to create the video. Instead, an audio file was created.")
                return

            subtitle_videos.append(subtitle_video)

            i +=1
        
        subtitle_videos = [VideoFileClip(video) for video in subtitle_videos]
        subtitle_main_video = concatenate_videoclips(subtitle_videos)
        subtitle_main_video.write_videofile(ouput_video, codec="libx264", audio_codec="aac")

    def create_audio(
            self, 
            ouput_audio : str,
            voice_settings : dict  = None,
            transcription_settings : dict = None,
            translate_settings : dict = None,
        ):

        if Path(ouput_audio).exists(): raise FileExistsError(f'The audio file {ouput_audio} already exists')

        # Validate whether the file is a audio
        if validate_media(file=ouput_audio) != "audio": raise InvalidFileType(f"The file '{ouput_audio}' is not a valid audio file.")

        extract_audio = self.__extract_audio(voice_settings, transcription_settings, translate_settings)

        merge_audios(audio_files=extract_audio[0], output=ouput_audio)