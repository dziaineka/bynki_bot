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
    BYN: [
        'BYN',
        'BYR',
        'зай',
        'бел',
        'бын',
        'быр',
        'Br',
    ],

    UAH: [
        'UAH',
        'гривен',
        'грыўняў',
        'укр',
        '₴',
    ],

    PLN: [
        'PLN',
        'злот',
        'пол',
        'zł',
    ],

    USD: [
        'USD',
        'дол',
        'бак',
        'през',
        'сша',
        '$',
    ],

    EUR: [
        'EUR',
        'евр',
        '€',
    ],

    RUB: [
        'RUB',
        'рос',
        '₽',
    ]
}
