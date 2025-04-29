import openai

class OpenAIConnection:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def connection_by_local_variable(self):
        openai.api_key = self.api_key
        return openai

    def connection_by_environment_variable(self):
        print("B")
        return openai.OpenAI()    

    def connection(self):
        if self.api_key is None:
            return self.connection_by_environment_variable()
        else:
            return self.connection_by_local_variable()

        