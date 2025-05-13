from pathlib import Path

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


class FileManager:
    def __init__(self, main_folder : str ="transvid0"):
        
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

    def create_structure(self):

        # Main folder
        self.create_main_folder()

        # Folders
        self.create_folder(self.audios_folder)
        self.create_folder(self.videos_folder)
        self.create_folder(self.transcriptions_folder)
    
    def check_path(self, file=str, folder=str):
        if not Path(f"{self.main_folder}/{folder}").exists(): 
            raise ValueError(f"Folder {self.main_folder}/{folder} not found")
        else:
            return Path(f"{self.main_folder}/{folder}/{file}")


    


