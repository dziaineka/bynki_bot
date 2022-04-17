import json
import logging
from datetime import datetime, timedelta
from typing import Optional

import aiohttp

import config

logger = logging.getLogger(__name__)


async def download_rates() -> Optional[dict]:
    logger.info('Загружаем валюты.')
    new_rates = dict()

    try:
        for currency_type in config.CURRENCIES:
            new_rates[currency_type] = \
                await _get_rate(currency_type)

        logger.info('Загрузили.')
        return new_rates
    except Exception:
        logger.exception("Error while loading exchange rates")
        return None


async def _get_rate(currency_type):
    if currency_type == config.BYN:
        return 1

    url = 'https://www.nbrb.by/API/ExRates/Rates/' + currency_type + '?'

    params = {
        'ParamMode': 2
    }

    try:
        async with aiohttp.ClientSession() as http_session:
            async with http_session.get(url, params=params) as response:
                if response.status != 200:
                    return None

                resp_json = await response.json(content_type=None)

                return \
                    resp_json['Cur_OfficialRate'] / resp_json['Cur_Scale']

    except aiohttp.ServerTimeoutError:
        return None

    except json.decoder.JSONDecodeError:
        return None

    except IndexError:
        return None
