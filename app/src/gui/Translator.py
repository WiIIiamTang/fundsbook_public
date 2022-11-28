import json

class Translator:
    '''
    Translates elements on the gui.
    Status messages and log message are NOT currently supported.

    Base language: en
    '''
    def __init__(self, initial_lang):
        self.base_lang = 'en'
        self.lang = initial_lang

    def get_translation_function(self):
        if self.lang != self.base_lang:
            with open(f'app/languages/lang_{self.lang}.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return lambda code: lambda s: data[code][s]
        else:
            return lambda code: lambda s: s
