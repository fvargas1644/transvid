from pathlib import Path
from datetime import timedelta
import ffmpeg
import subprocess
from moviepy import concatenate_audioclips, AudioFileClip
from errors import InvalidFileType

def validate_media(file: str):
    # Extensiones válidas para audio y video
    audio_extensions = {'.mp3', '.wav', '.aac', '.ogg', '.flac', '.m4a'}
    video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'}

    extension = Path(file).suffix.lower()

    # Determinar si es un archivo de audio o video basado en la extensión
    if extension in audio_extensions:
        return "audio"
    elif extension in video_extensions:
        return "video"
    else:
        raise InvalidFileType(f"The file '{path}' is not a valid audio or video file.")

def merge_audios(audio_files : list[str], output : str ="final_audio.mp3"):
    """
    Merges multiple audio files into a single one.

    :param audio_files: List of paths to audio files (in order)
    :param output: Name of the output file (with extension)
    """
    try:
        clips = [AudioFileClip(audio) for audio in audio_files]
        final_audio = concatenate_audioclips(clips)
        final_audio.write_audiofile(output)
        print(f"✅ Audio successfully exported to: {output}")
    except Exception as e:
        print(f"❌ Error while merging audios: {e}")

def create_video_with_audio(output_video :str, audio_file :str, resolution="1280x720"):
    """
    Creates a black video with the specified resolution and overlays the given audio file.
    
    Parameters:
    - output_video: Name of the output video file 
    - audio_file: Path to the input audio file 
    - resolution: Resolution of the black video background (default is "1280x720")
    """
    command = [
        "ffmpeg",
        "-f", "lavfi",
        "-i", f"color=c=black:s={resolution}",
        "-i", audio_file,
        "-shortest",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        output_video
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"Video successfully created: {output_video}")
        return True
    
    except subprocess.CalledProcessError as e:
        print("Error while executing ffmpeg:", e)
        return False


def embed_subtitles(input_video : str, subtitles_file :str, output_video : str, font_size : int=30, alignment : int=8):
    """
    Embeds subtitles into a video using ffmpeg.

    Parameters:
    - input_video (str): Path to the input video file.
    - subtitles_file (str): Path to the subtitle file (.srt).
    - output_video (str): Path to the output video file.
    - font_size (int, optional): Font size for the subtitles.
    - alignment (int, optional): Subtitle alignment (8 = top center, 2 = bottom center, etc.).
    """
    command = [
        "ffmpeg",
        "-i", input_video,
        "-vf", f"subtitles={subtitles_file}:force_style='FontSize={font_size},Alignment={alignment}'",
        output_video
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Video successfully created: {output_video}")
        return True
    except subprocess.CalledProcessError as e:
        print("Error running ffmpeg:", e)
        return False

def change_file_format(input_file : str, output_file : str):

    input_path = Path(input_file)

    output_path = Path(output_file)

    try:
        (
            ffmpeg
            .input(str(input_path))
            .output(str(output_path))
            .run(overwrite_output=True)
        )

        return output_path
    except ffmpeg.Error as e:
        raise ValueError("An error occurred during conversion:", e)


def divide_text_into_parts(text : str, maximum_length : int= 13000):
    text_parts = []
    start = 0
    while start < len(text):
        end = start + maximum_length

        if end >= len(text):
            text_parts.append(text[start:].strip())
            break

        cutting = text.rfind(". ", start, end + 1)
        if cutting == -1 or cutting <= start:
            cutting = end
        else:
            cutting += 2  

        text_parts.append(text[start:cutting])
        start = cutting

    return text_parts

def format_timestamp_for_srt_files(seconds):
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    millis = int((td.total_seconds() - int(td.total_seconds())) * 1000)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{millis:03d}"

class FileManager:
    def __init__(self, main_folder : str = "transvid0"):
        
        # Main folder
        self.main_folder = main_folder

        # Folders
        self.audios_folder = f"{self.main_folder}/audios"
        self.videos_folder = f"{self.main_folder}/videos"
        self.transcriptions_folder = f"{self.main_folder}/transcriptions"

    def create_main_folder(self):
        i = 0
        while True:
            folder = Path(f"transvid{i}")
            if not folder.exists():
                folder.mkdir()
                self.main_folder = folder
                break
            i+=1

    def create_folder(self, name : str):
        folder=Path(name)

        if not folder.exists(): 
            folder.mkdir()

        return folder

    def create_structure(self):

        # Main folder
        self.create_main_folder()

        # Folders
        self.audios_folder = self.create_folder(f'{self.main_folder}/audios')
        self.videos_folder = self.create_folder(f'{self.main_folder}/videos')
        self.transcriptions_folder = self.create_folder(f'{self.main_folder}/transcriptions')
    
    def check_path(self, path : str):

        path = Path(path)

        if  not path.exists(): 
            raise ValueError(f"Path {path} not found")
        else:
            return path
        
    """Create a non-existing folder in the current path if create_in is None, otherwise create the folder in the folder mentioned in create_in"""
    def create_dynamic_folder(self, create_in : str = None):
        folder_path = Path(create_in) if create_in != None else None

        if create_in != None:
            if not folder_path.exists(): 
                raise ValueError(f"Folder {folder_path} not found")
        
        i=0
        while True:
            new_folder = Path(f"{create_in}/{i}") if create_in != None else Path(f"{i}")
            if not new_folder.exists():
                new_folder.mkdir()
                return new_folder
            
            i+=1

    def path_components(self, path : str):
        path=Path(path)

        folder = str(path.parent) 
        filename = str(path.stem) 
        extension_file = path.suffix.lstrip('.')

        return folder, filename, extension_file