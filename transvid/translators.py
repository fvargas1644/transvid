from googletrans import Translator
import deepl


class Translators:
    def __init__(self, text: str, target_lang='es', source_lang=None):
        self.target_lang = target_lang
        self.source_lang = source_lang
        self.text = text
    
    def obtain_kwargs(self, key_target_lang, key_source_lang):
        kwargs = {key_target_lang: self.target_lang}

        if self.source_lang:
            kwargs[key_source_lang] = self.source_lang
        
        return kwargs

    async def translate_with_googletrans(self):
        translator  = Translator()
        kwargs = self.obtain_kwargs(key_target_lang='dest', key_source_lang='src')
        translation = await translator.translate(self.text, **kwargs)
        return translation

    def translate_with_deepl(self, auth_key):
        translator = deepl.Translator(auth_key)
        kwargs = self.obtain_kwargs(key_target_lang='target_lang', key_source_lang='source_lang')
        translation = translator.translate_text(self.text, **kwargs)
        return translation