from App.Core.Abstract.AbstractSeeder import AbstractSeeder
from App.Models.Client.Language import Language


LANGUAGES = [
    'English',
    'Russian',
    'Azeri Latin',
    'Bashkir',
    'Bulgarian',
    'Catalan',
    'Croatian',
    'Czech',
    'Danish',
    'Dutch',
    'Dutch Belgian',
    'Estonian',
    'Finnish',
    'French',
    'German',
    'German New Spelling',
    'Hebrew',
    'Hungarian',
    'Indonesian',
    'Italian',
    'Korean',
    'Korean Hangul',
    'Latvian',
    'Lithuanian',
    'Norwegian Bokmal',
    'Norwegian Nynorsk',
    'Polish',
    'Portuguese Brazilian',
    'Portuguese Standard',
    'Romanian',
    'Slovak',
    'Slovenian',
    'Spanish',
    'Swedish',
    'Tatar',
    'Turkish',
    'Ukrainian',
    'Vietnamese',
]


class LanguagesSeeder(AbstractSeeder):
    def run(self):
        Language.query().delete()

        for language in LANGUAGES:
            Language.create(name=language.replace(" ", "_").lower())
