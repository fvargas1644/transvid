import openai

class OpenAIConnection:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def connection_by_local_variable(self):
        openai.api_key = self.api_key
        return openai

    def connection_by_environment_variable(self):
        return openai.OpenAI()    

    def connection(self):
        if self.api_key is None:
            return self.connection_by_environment_variable()
        else:
            return self.connection_by_local_variable()

class TextToAudioToModel(OpenAIConnection):
    def __init__(self, input, api_key=None, model="tts-1", voice="onyx", instructions ="", response_format="mp3", speed=1):
        super().__init__(api_key)
        self.client = self.connection()
        self.request_body = {
            "input": input,
            "model" : model,
            "voice" : voice,
            "instructions" : instructions,
            "response_format" : response_format,
            "speed" : speed,
        }

    def run_model(self):
        return self.connection().audio.speech.create(**self.request_body)
