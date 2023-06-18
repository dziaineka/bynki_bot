import logging
from typing import Optional

import aiohttp
import config

logger = logging.getLogger(__name__)


async def download_rates() -> Optional[dict]:
    logger.info("Загружаем валюты.")
    new_rates = dict()

    try:
        for currency_type in config.CURRENCIES:
            currency_rate = await _get_rate(currency_type)

            if currency_rate is None:
                raise Exception(
                    f"NBRB getrate returns None for currency {currency_type}"
                )

            new_rates[currency_type] = currency_rate

        logger.info("Загрузили.")
        return new_rates
    except Exception:
        logger.exception("Error while loading exchange rates")
        return None


async def _get_rate(currency_type):
    if currency_type == config.BYN:
        return 1

    url = f"https://api.nbrb.by/exrates/rates/{currency_type}?parammode=2"

    async with aiohttp.ClientSession() as http_session:
        async with http_session.get(url) as response:
            if response.status != 200:
                raise Exception(
                    f"get rates response status is {response.status}"
                )

            resp_json = await response.json(content_type=None)

            return resp_json["Cur_OfficialRate"] / resp_json["Cur_Scale"]
