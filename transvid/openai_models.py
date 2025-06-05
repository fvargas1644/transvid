from openai import OpenAI
import whisper
from utils import FileManager

def create_openai_client(api_key=None):
    """Return an OpenAI client using a provided API key or the environment's key"""
    return OpenAI(api_key=api_key) if api_key else OpenAI()

class TextToAudioModels:
    def __init__(
        self,
        text: str,
        api_key: str = None,
        model: str = "tts-1",
        voice: str = "onyx",
        instructions: str = "",
        response_format: str = "wav",
        speed: float = 1.0,
    ):
        self.client = create_openai_client(api_key)
        self.params = {
            "input": text,
            "model": model,
            "voice": voice,
            "instructions": instructions,
            "response_format": response_format,
            "speed": speed,
        }

        self.response_format = response_format

    def create_audio(self, file_name : str):
        
        file = f'{file_name}.{self.response_format}'

        with self.client.audio.speech.with_streaming_response.create(**self.params) as response:
            response.stream_to_file(file)
        
        return file

class LocalWhisperModel:
    def __init__(self,file : str,  model="turbo" ):
        self.model = model
        self.client = self.load_model()
        self.file = file

    def load_model(self):
        return whisper.load_model(self.model)
    
    def transcribe(self):
        return self.client.transcribe(audio=self.file)

