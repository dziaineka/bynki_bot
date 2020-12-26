import asyncio
import logging
import re
import sys
from typing import List, Tuple, Union

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.utils.exceptions import MessageNotModified

import config
import regexps
from exchanger import Exchanger

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger("bynki_bot")

loop = asyncio.get_event_loop()

bot = Bot(token=config.BOT_TOKEN, loop=loop)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
exchanger = Exchanger()

re_float = re.compile(regexps.re_float,
                      re.MULTILINE | re.IGNORECASE | re.VERBOSE)

re_parse = re.compile(regexps.re_parse,
                      re.MULTILINE | re.IGNORECASE | re.VERBOSE)

ARITHMETIC_OPERATIONS = ['+', '-', '*', '/']
WRONG_INPUT = 'Некорректный ввод 🤷‍♀️'


def keywords_match(raw_input: str, keywords: list) -> bool:
    for keyword in keywords:
        if keyword.upper() in raw_input.upper():
            return True

    return False


def parse_input(raw_input: str) -> list:
    raw_input = raw_input.replace(',', '.').replace(' ', '')
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

    for currency_type in config.KEYWORDS:
        if keywords_match(user_string, config.KEYWORDS[currency_type]):
            return get_amount(user_string), currency_type

    return get_amount(user_string), config.BYN


def compose_reply(amounts, main_currency):
    text = formatted_sum(amounts, main_currency) + '\n'

    del amounts[main_currency]

    for currency_type in amounts:
        text += formatted_sum(amounts, currency_type)

    return text.replace(',', ' ')


def formatted_sum(amounts: dict, currency: str) -> str:
    amount = amounts[currency]

    if isinstance(amount, float):
        amount = f'{amount:,}'

    return f'{config.FLAGS[currency]} <b>{amount}</b> \n'


def get_currency_button(currency_type):
    button = types.InlineKeyboardButton(
        text=f'{config.FLAGS[currency_type]} {currency_type}',
        callback_data=currency_type)

    return button


def compose_keyboard(excluded_currency):
    # настроим клавиатуру
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    buttons = list()

    for currency_type in config.CURRENCIES:
        buttons.append(get_currency_button(currency_type))

    return keyboard.add(*buttons)


async def exhange(
        amount: float,
        currency_from: str) -> Tuple[str, types.InlineKeyboardMarkup]:
    exchanged_amount = await exchanger.exchange(amount, currency_from)
    text = compose_reply(exchanged_amount, currency_from)
    keyboard = compose_keyboard(currency_from)
    return text, keyboard


def get_amount(message_text):
    m = re_float.findall(message_text.replace(' ', ''))
    return float(m[0][0])


def valid_input(raw_input):
    m = re_float.findall(raw_input)

    if m:
        return True


async def calc_and_exhange(
        pieces: list) -> Tuple[str, types.InlineKeyboardMarkup]:
    exhanged_pieces = ''

    for piece in pieces:
        if not isinstance(piece, tuple) and piece in ARITHMETIC_OPERATIONS:
            exhanged_pieces += piece
            continue

        exchanged_amount = await exchanger.exchange(*piece)
        exhanged_pieces += str(exchanged_amount[config.BYN])

    success, calculated = calc(exhanged_pieces)

    if success:
        text, keyboard = await exhange(calculated, config.BYN)
    else:
        text = WRONG_INPUT
        keyboard = None

    return text, keyboard


def calc(str_to_eval: str) -> Tuple[bool, float]:
    sum = 0
    success = False

    try:
        sum = eval(str_to_eval)
        success = True
    finally:
        return success, sum


async def make_exhanging(text: str) -> Tuple[str, types.InlineKeyboardMarkup]:
    parsed_input = parse_input(text)

    if len(parsed_input) == 1:
        data_to_convert = parsed_input.pop()
        text, keyboard = await exhange(*data_to_convert)
    else:
        text, keyboard = await calc_and_exhange(parsed_input)

    return text, keyboard


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    """
    Conversation's entry point
    """
    logger.info('Пришел новый пользователь.' + str(message.from_user.username))
    await message.reply('Привет, вводи сумму и я конвертирую ее в ' +
                        'валюты наших соседей.')


@dp.message_handler(lambda message: valid_input(message.text),
                    content_types=types.ContentType.TEXT)
async def amount_sent(message: types.Message):
    """
    Process entered money amount
    """
    logger.info(f'Спросили сумму "{message.text}" - ' +
                str(message.from_user.username))

    text, keyboard = await make_exhanging(message.text)

    await bot.send_message(message.from_user.id,
                           text,
                           reply_markup=keyboard,
                           parse_mode='HTML')


@dp.inline_handler()
async def inline_exhange(inline_query: types.InlineQuery):
    logger.info(f'Спрашивают инлайн {inline_query.query} ' +
                str(inline_query.from_user.username))

    input_content = types.InputTextMessageContent(inline_query.query,
                                                  parse_mode='HTML')

    text = WRONG_INPUT

    if valid_input(input_content.message_text):
        text, _ = await make_exhanging(input_content.message_text)
        input_content.message_text = text
    else:
        input_content.message_text = WRONG_INPUT

    item = types.InlineQueryResultArticle(id='1',
                                          title=text.replace('*', ''),
                                          input_message_content=input_content)

    await bot.answer_inline_query(inline_query.id, results=[item])


@dp.message_handler()
async def wrong_input(message: types.Message):
    """
    Wrong input
    """
    logger.info(f'Спросили неправильное "{message.text}" - ' +
                str(message.from_user.username))

    await bot.send_message(message.from_user.id, WRONG_INPUT)


@dp.callback_query_handler(lambda call: call.data in config.CURRENCIES)
async def currency_click(call):
    logger.info('Обрабатываем нажатие кнопки другой валюты - ' +
                str(call.from_user.username))

    await bot.answer_callback_query(call.id)
    text, keyboard = await exhange(get_amount(call.message.text), call.data)

    try:
        await bot.edit_message_text(text,
                                    call.message.chat.id,
                                    call.message.message_id,
                                    reply_markup=keyboard,
                                    parse_mode='HTML')
    except MessageNotModified:
        pass


async def startup(dispatcher: Dispatcher):
    logger.info('Загружаем валюты.')
    await exchanger.download_rates()
    logger.info('Загрузили.')


if __name__ == '__main__':
    executor.start_polling(dp,
                           loop=loop,
                           skip_updates=True,
                           on_startup=startup)
