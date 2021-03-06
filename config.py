import os


BOT_TOKEN = os.getenv('TG_TOKEN')

# currencies
BYN = 'BYN'
UAH = 'UAH'
PLN = 'PLN'
USD = 'USD'
EUR = 'EUR'
RUB = 'RUB'

FLAGS = {
    BYN: '🇧🇾',
    UAH: '🇺🇦',
    PLN: '🇵🇱',
    USD: '🇺🇸',
    EUR: '🇪🇺',
    RUB: '🇷🇺'
}

CURRENCIES = list(FLAGS)

FULL_MATCH = 'full_match'
INSIDE = 'inside'

KEYWORDS = {
    INSIDE: {
        UAH: [
            'UAH',
            'грив',
            'гры',
            'укр',
            '₴',
            'ukr',
            'hryv',
            'hriv',
            'griv',
        ],

        PLN: [
            'PLN',
            'злот',
            'пол',
            'zł',
            'zl',
            'pol',
        ],

        USD: [
            'USD',
            'дол',
            'dol',
            'бак',
            'през',
            'сша',
            'usa',
            '$',
            'amer',
        ],

        EUR: [
            'EUR',
            'евр',
            'эвр',
            '€',
            'eu',
        ],

        RUB: [
            'RUB',
            'рос',
            'рус',
            'раш',
            '₽',
            'дерев',
            'rus',
            'ros',
        ]
    },
    FULL_MATCH: {
        UAH: [
            'у',
            'u',
            'г',
            'g',
            'h',
        ],

        PLN: [
            'п',
            'p',
            'з',
            'z',
        ],

        USD: [
            'a',
            'а',
            'd',
            'д',
        ],

        EUR: [
            'е',
            'e',
        ],

        RUB: [
            'рф',
            'rf',
            'ру',
            'ru',
        ]
    }
}
