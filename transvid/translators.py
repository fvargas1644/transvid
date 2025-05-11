from googletrans import Translator
import deepl
from utils import divide_text_into_parts
import asyncio


class TextTranslators:
    def __init__(self, text: str, target_lang : str='es', source_lang : str =None):
        self.target_lang = target_lang
        self.source_lang = source_lang
        self.text = text
    
    def obtain_kwargs(self, key_target_lang, key_source_lang):
        kwargs = {key_target_lang: self.target_lang}

        if self.source_lang:
            kwargs[key_source_lang] = self.source_lang
        
        return kwargs

    async def translate_with_googletrans(self,text : str=None):
        translator  = Translator()
        kwargs = self.obtain_kwargs(key_target_lang='dest', key_source_lang='src')
        translation = await translator.translate(text if text else self.text, **kwargs)
        return translation.text

    def translate_with_deepl(self, auth_key, text : str=None):
        translator = deepl.Translator(auth_key)
        kwargs = self.obtain_kwargs(key_target_lang='target_lang', key_source_lang='source_lang')
        translation = translator.translate_text(text if text else self.text, **kwargs)
        return translation.text

    def translate(self, auth_key : str = None, translator : str="googletrans"):
        
        if translator == "googletrans" :
            text_divided_into_parts = divide_text_into_parts(self.text, maximum_length=13000) 
        elif translator == "deepl": 
            text_divided_into_parts = divide_text_into_parts(self.text, maximum_length=4000)
        
        all_text = ""
        for text_part in text_divided_into_parts:
            if translator == "googletrans" :
                all_text += asyncio.run(self.translate_with_googletrans(text=text_part))
            elif translator == "deepl": 
                all_text += self.translate_with_deepl(text=text_part,auth_key=auth_key) 
        
        return all_text