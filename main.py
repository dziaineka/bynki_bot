import asyncio
import config
import logging
import regexps
import re
from exchanger import Exchanger
from typing import Optional

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode
from aiogram.utils import executor


def setup_logging():
    # create logger
    my_logger = logging.getLogger('parkun_log')
    my_logger.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    ch.setFormatter(formatter)

    # add the handlers to the logger
    my_logger.addHandler(ch)

    return my_logger


loop = asyncio.get_event_loop()

bot = Bot(token=config.BOT_TOKEN, loop=loop)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
exchanger = Exchanger()
logger = setup_logging()

re_float = re.compile(regexps.re_float,
                      re.MULTILINE | re.IGNORECASE | re.VERBOSE)


def parse_input(raw_input):
    return raw_input, config.BYN


def compose_reply(amounts, main_currency):
    text = f'{config.FLAGS[main_currency]} {amounts[main_currency]} \n\n'
    del amounts[main_currency]

    for currency_type in amounts:
        text += f'{config.FLAGS[currency_type]} {amounts[currency_type]} \n'

    return text


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


def exhange(amount, currency_from):
    exchanged_amount = exchanger.exchange(amount, currency_from)
    text = compose_reply(exchanged_amount, currency_from)
    keyboard = compose_keyboard(currency_from)
    return text, keyboard


def get_amount(message_text):
    clean_text = message_text.replace('\n', '|').replace(' ', '|')
    m = re_float.findall(clean_text)
    return float(m[0][0])


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    """
    Conversation's entry point
    """
    logger.info('Пришел новый пользователь.' + str(message.from_user.username))
    await message.reply('Привет, вводи сумму и я конвертирую ее в ' +
                        'валюты наших соседей.')


@dp.message_handler(content_types=types.ContentType.TEXT)
async def amount_sent(message: types.Message, state: FSMContext):
    """
    Process entered money amount
    """
    logger.info(f'Спросили сумму "{message.text}" - ' +
                str(message.from_user.username))

    amount, currency_type = parse_input(message.text)
    text, keyboard = exhange(amount, currency_type)
    await bot.send_message(message.from_user.id, text, reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data in config.CURRENCIES)
async def currency_click(call):
    logger.info('Обрабатываем нажатие кнопки другой валюты - ' +
                str(call.from_user.username))

    await bot.answer_callback_query(call.id)
    text, keyboard = exhange(get_amount(call.message.text), call.data)

    await bot.edit_message_text(text,
                                call.message.chat.id,
                                call.message.message_id,
                                reply_markup=keyboard)


async def startup(dispatcher: Dispatcher):
    logger.info('Загружаем валюты.')
    await exchanger.download_currencies()
    logger.info('Загрузили.')


if __name__ == '__main__':
    executor.start_polling(dp,
                           loop=loop,
                           skip_updates=True,
                           on_startup=startup)
