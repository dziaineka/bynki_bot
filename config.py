from os import getenv
from os.path import join, dirname
from dotenv import load_dotenv

# Create .env file path.
dotenv_path = join(dirname(__file__), ".env")

# Load file from the path.
load_dotenv(dotenv_path)


BOT_TOKEN = getenv("TG_TOKEN", "")
ENABLE_DUMMY_SERVER = bool(int(getenv("ENABLE_DUMMY_SERVER", 0)))

# hours
REFRESH_RATES_INTERVAL = int(getenv("REFRESH_RATES_INTERVAL", "1"))
# hours
RATES_TTL = int(getenv("RATES_TTL", "4"))

# currencies
BYN = "BYN"
UAH = "UAH"
PLN = "PLN"
USD = "USD"
EUR = "EUR"
RUB = "RUB"
GEL = "GEL"
AMD = "AMD"
TRY = "TRY"

FLAGS = {
    BYN: "🇧🇾",
    UAH: "🇺🇦",
    PLN: "🇵🇱",
    USD: "🇺🇸",
    EUR: "🇪🇺",
    RUB: "🇷🇺",
    GEL: "🇬🇪",
    AMD: "🇦🇲",
    TRY: "🇹🇷",
}

CURRENCIES = list(FLAGS)

FULL_MATCH = "full_match"
INSIDE = "inside"

KEYWORDS = {
    INSIDE: {
        UAH: [
            "UAH",
            "грив",
            "гры",
            "укр",
            "₴",
            "ukr",
            "hryv",
            "hriv",
            "griv",
        ],
        PLN: [
            "pl",
            "pol",
            "зл",
            "пол",
            "пл",
            "zł",
            "zl",
        ],
        USD: [
            "USD",
            "дол",
            "dol",
            "бак",
            "през",
            "сша",
            "usa",
            "$",
            "amer",
        ],
        EUR: [
            "EUR",
            "евр",
            "эвр",
            "€",
            "eu",
        ],
        RUB: [
            "RUB",
            "рос",
            "рус",
            "раш",
            "₽",
            "дерев",
            "rus",
            "ros",
        ],
        GEL: [
            "лар",
            "гру",
            "ge",
            "lar",
            "გე",
            "sak",
            "sk",
        ],
        AMD: [
            "арм",
            "др",
            "arm",
            "dr",
            "am",
            "հայ",
        ],
        TRY: [
            "тур",
            "лир",
            "tur",
            "lir",
            "tr",
            "₺",
        ],
    },
    FULL_MATCH: {
        UAH: [
            "у",
            "u",
            "г",
            "g",
            "h",
        ],
        PLN: [
            "п",
            "p",
            "з",
            "z",
        ],
        USD: [
            "a",
            "а",
            "d",
            "д",
        ],
        EUR: [
            "е",
            "e",
        ],
        RUB: [
            "рф",
            "rf",
            "ру",
            "ru",
        ],
    },
}
