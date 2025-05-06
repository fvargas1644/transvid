import openai
from openai import OpenAI
import whisper

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
        response_format: str = "mp3",
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

    def run_model(self):
        return self.client.audio.speech.create(**self.params)

class LocalWhisperModel:
    def __init__(self, model="trubo"):
        self.model = model
        self.client = self.load_model()

    def load_model(self):
        whisper.load_model(self.model)

