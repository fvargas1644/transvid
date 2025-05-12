from googletrans import Translator
import deepl
from utils import divide_text_into_parts
import asyncio
from openai_models import LocalWhisperModel, TextToAudioModels


class TextTranslators:
    def __init__(self, target_lang : str='es', source_lang : str =None):
        self.target_lang = target_lang
        self.source_lang = source_lang
    
    def obtain_kwargs(self, key_target_lang, key_source_lang):
        kwargs = {key_target_lang: self.target_lang}

        if self.source_lang:
            kwargs[key_source_lang] = self.source_lang
        
        return kwargs

    async def __translate_with_googletrans(self,text : str):
        translator  = Translator()
        kwargs = self.obtain_kwargs(key_target_lang='dest', key_source_lang='src')
        translation = await translator.translate(text, **kwargs)
        return translation.text

    def __translate_with_deepl(self, auth_key, text : str):
        translator = deepl.Translator(auth_key)
        kwargs = self.obtain_kwargs(key_target_lang='target_lang', key_source_lang='source_lang')
        translation = translator.translate_text(text, **kwargs)
        return translation.text

    def translate(self,text : str, auth_key : str = None, translator : str="googletrans"):
        
        if translator == "googletrans" :
            text_divided_into_parts = divide_text_into_parts(text, maximum_length=13000) 
        elif translator == "deepl": 
            text_divided_into_parts = divide_text_into_parts(text, maximum_length=4000)
        
        all_text = ""
        for text_part in text_divided_into_parts:
            if translator == "googletrans" :
                all_text += asyncio.run(self.__translate_with_googletrans(text=text_part))
            elif translator == "deepl": 
                all_text += self.__translate_with_deepl(text=text_part,auth_key=auth_key) 
        
        return all_text

class TranslateAudio(TextTranslators):
    def __init__(self, file: str, target_lang : str='es', source_lang : str =None):
        self.file = file
        super().__init__(target_lang=target_lang, source_lang=source_lang)

    def transcribe_with_local_whisper_model(self, model : str="turbo"):
        transcription = LocalWhisperModel(model, file=self.file)
        return transcription.transcribe()

    def convert_text_to_audio_with_openai(
        self, 
        text: str,  
        api_key: str = None,
        model: str = "tts-1",
        voice: str = "onyx",
        instructions: str = "",
        response_format: str = "mp3",
        speed: float = 1.0
    ):
        text_to_audio = TextToAudioModels(
            text=text, 
            api_key=api_key, 
            model=model, 
            voice=voice, 
            instructions=instructions,
            response_format=response_format,
            speed= speed
        )

        text_to_audio.create_audio("audio")
