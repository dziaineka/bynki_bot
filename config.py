BOT_TOKEN = "PASTE_TOKEN_HERE"

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

KEYWORDS = {
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
}
