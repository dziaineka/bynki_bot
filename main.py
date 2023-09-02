import asyncio
import logging
import re
import sys
from typing import List, Optional, Tuple, Union

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder


import config
import dummy_server
import regexps
from exchanger import Exchanger

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("bynki_bot")

bot = Bot(config.BOT_TOKEN, parse_mode=ParseMode.HTML)

dp = Dispatcher()
exchanger = Exchanger()

re_float = re.compile(
    regexps.re_float, re.MULTILINE | re.IGNORECASE | re.VERBOSE
)

re_parse = re.compile(
    regexps.re_parse, re.MULTILINE | re.IGNORECASE | re.VERBOSE
)

ARITHMETIC_OPERATIONS = ["+", "-", "*", "/"]
WRONG_INPUT = "Некарэктны ўвод 🤷‍♀️"


def keywords_inside(raw_input: str, keywords: list) -> bool:
    for keyword in keywords:
        if keyword.upper() in raw_input.upper():
            return True

    return False


def keywords_full_match(raw_input: str, keywords: list) -> bool:
    amount = get_amount(raw_input)
    currency_only = raw_input.replace(str(amount), "")
    currency_only = raw_input.replace(str(int(amount)), "")
    currency_only = currency_only.replace(".", "")

    for keyword in keywords:
        if keyword.upper() == currency_only.upper():
            return True

    return False


def parse_input(raw_input: str) -> list:
    raw_input = raw_input.replace(",", ".").replace(" ", "")
    points_count = raw_input.count(".")
    raw_input = raw_input.replace(".", "", points_count - 1)
    splitted_input = split_input(raw_input)
    parsed_input = list()

    for input_piece in splitted_input:
        recognized = recognize_currency(input_piece)

        if recognized:
            parsed_input.append(recognized)

    return parsed_input


def split_input(raw_input: str) -> List[str]:
    findall = re_parse.findall(raw_input)
    splitted_input = list()

    for piece in findall:
        splitted_input += list(piece)

    cleaned_input = list()

    for piece in splitted_input:
        if piece:
            cleaned_input.append(piece)

    return cleaned_input


def recognize_currency(user_string: str) -> Union[tuple, str]:
    if user_string in ARITHMETIC_OPERATIONS:
        return user_string

    full_match_patterns = config.KEYWORDS[config.FULL_MATCH]

    for currency_type in full_match_patterns:
        if keywords_full_match(
            user_string, full_match_patterns[currency_type]
        ):
            return get_amount(user_string), currency_type

    inside_patterns = config.KEYWORDS[config.INSIDE]

    for currency_type in inside_patterns:
        if keywords_inside(user_string, inside_patterns[currency_type]):
            return get_amount(user_string), currency_type

    return get_amount(user_string), config.BYN


def compose_reply(amounts, main_currency):
    text = formatted_sum(amounts, main_currency) + "\n"

    del amounts[main_currency]

    for currency_type in amounts:
        text += formatted_sum(amounts, currency_type)

    return text.replace(",", " ")


def formatted_sum(amounts: dict, currency: str) -> str:
    amount = amounts[currency]

    if isinstance(amount, float):
        amount = f"{amount:,}"

    return f"{config.FLAGS[currency]} <b>{amount}</b> \n"


def get_currency_button(currency_type: str) -> types.InlineKeyboardButton:
    text = f"{config.FLAGS[currency_type]} {currency_type}"

    button = types.InlineKeyboardButton(
        text=text,
        callback_data=currency_type,
    )  # type: ignore

    return button


def compose_keyboard() -> types.InlineKeyboardMarkup:
    # настроим клавиатуру
    keyboard = InlineKeyboardBuilder()
    buttons = list()

    for currency_type in config.CURRENCIES:
        buttons.append(get_currency_button(currency_type))

    return keyboard.add(*buttons).adjust(3, repeat=True).as_markup()


async def exhange(
    amount: float, currency_from: str
) -> Tuple[str, types.InlineKeyboardMarkup]:
    exchanged_amount = await exchanger.exchange(amount, currency_from)
    text = compose_reply(exchanged_amount, currency_from)
    keyboard = compose_keyboard()
    return text, keyboard


def get_amount(message_text):
    m = re_float.findall(message_text.replace(" ", ""))
    return float(m[0][0])


def valid_input(raw_input):
    m = re_float.findall(raw_input)

    if m:
        return True


async def calc_and_exhange(
    pieces: list,
) -> Tuple[str, Optional[types.InlineKeyboardMarkup]]:
    exhanged_pieces = ""
    preferred_currency = get_preferred_currency(pieces)

    for piece in pieces:
        if not isinstance(piece, tuple) and piece in ARITHMETIC_OPERATIONS:
            exhanged_pieces += piece
            continue

        exchanged_amount = await exchanger.exchange(*piece)
        exhanged_pieces += str(exchanged_amount[preferred_currency])

    success, calculated = calc(exhanged_pieces)

    if success:
        text, keyboard = await exhange(calculated, preferred_currency)
    else:
        text = WRONG_INPUT
        keyboard = None

    return text, keyboard


def get_preferred_currency(bundles: List[tuple]) -> str:
    for bundle in bundles:
        try:
            return bundle[1]
        except IndexError:
            continue

    return config.BYN


def calc(str_to_eval: str) -> Tuple[bool, float]:
    sum = 0
    success = False

    try:
        sum = eval(str_to_eval)
        sum = round(sum, 2)
        success = True
    finally:
        return success, sum


async def make_exhanging(
    text: str | None,
) -> Tuple[str, Optional[types.InlineKeyboardMarkup]]:
    if text is None:
        return WRONG_INPUT, None

    parsed_input = parse_input(text)

    if len(parsed_input) == 1:
        data_to_convert = parsed_input.pop()
        text, keyboard = await exhange(*data_to_convert)
    else:
        text, keyboard = await calc_and_exhange(parsed_input)

    return text, keyboard


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """
    Conversation's entry point
    """
    logger.info("New user." + str(message.from_user.username))
    await message.reply(
        "Прывітанне, уводзь суму і я канвертую яе ў іншыя валюты."
    )


@dp.message(F.text, lambda message: valid_input(message.text))
async def amount_sent(message: types.Message):
    """
    Process entered money amount
    """
    logger.info(
        f'Sum asked "{message.text}" - ' + str(message.from_user.username)
    )

    text, keyboard = await make_exhanging(message.text)

    await bot.send_message(
        message.from_user.id, text, reply_markup=keyboard, parse_mode="HTML"
    )


@dp.message()
async def wrong_input(message: types.Message):
    """
    Wrong input
    """
    logger.info(
        f'Wrong asked "{message.text}" - ' f"{str(message.from_user.username)}"
    )

    await bot.send_message(message.from_user.id, WRONG_INPUT)


@dp.callback_query(lambda call: call.data in config.CURRENCIES)
async def currency_click(call):
    logger.info(
        f"Currency button handling "
        f"{call.data} - {str(call.from_user.username)}"
    )

    await bot.answer_callback_query(call.id)
    text, keyboard = await exhange(get_amount(call.message.text), call.data)

    try:
        await bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
    except Exception as exception:
        print(exception)
        pass


@dp.startup()
async def startup(dispatcher: Dispatcher):
    asyncio.create_task(exchanger.update_rates())

    if config.ENABLE_DUMMY_SERVER:
        dummy_server.run()


async def main() -> None:
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
