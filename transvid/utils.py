from pathlib import Path
from datetime import timedelta
import ffmpeg
import subprocess

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


def convert_to_mkv(input_file, output_file=None):
    """
    Converts any video format to MKV using ffmpeg.

    :param input_file: Path to the input video file.
    :param output_file: (Optional) Path to the output MKV file. If not specified, 
                        the output will have the same name with .mkv extension.
    """
    input_path = Path(input_file)

    if output_file is None:
        output_path = input_path.with_suffix('.mkv')
    else:
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
    
    def check_path(self, file=str, folder=str):

        folder_path = Path(f"{folder}")

        if  not folder_path.exists(): 
            raise ValueError(f"Folder {folder_path} not found")
        else:
            return Path(f"{folder_path}/{file}")
        
    def check_file(self, file=str):

        file_path = Path(f"{file}")

        if  not file_path.is_file(): 
            raise FileNotFoundError(f"File {file_path} not found")
        else:
            return file_path
        
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