import asyncio
import json
import logging
from datetime import datetime, timedelta

import aiohttp

import config

NO_RATES = '🤷‍♀️ НБРБ не отдал курс'
logger = logging.getLogger(__name__)


class Exchanger:
    def __init__(self):
        self._rates = dict()
        self._rates_expiration = datetime.utcnow()
        self._download_task = None

    async def _get_rate(self, currency_type):
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

    def _set_expiration_time(self):
        next_day = datetime.utcnow() + timedelta(days=1)
        self._rates_expiration = datetime(next_day.year,
                                          next_day.month,
                                          next_day.day, 9, 0, 0)

    async def prepare_rates(self, force=False):
        if self._rates_expiration < datetime.utcnow():
            await self.download_rates()

        if not force:
            return

        if not isinstance(self._download_task, asyncio.Task):
            self._download_task = asyncio.create_task(self.download_rates())
            return

        try:
            self._download_task.result()
            self._download_task = asyncio.create_task(self.download_rates())
        except asyncio.CancelledError:
            self._download_task = asyncio.create_task(self.download_rates())
        except asyncio.InvalidStateError:
            logger.info("Уже загружаются")
            pass

    async def download_rates(self):
        try:
            for currency_type in config.CURRENCIES:
                self._rates[currency_type] = await self._get_rate(currency_type)

            self._set_expiration_time()
        except Exception:
            logger.exception("Error while loading exchange rates")

    async def exchange(self, amount: float, currency_from: str) -> dict:
        await self.prepare_rates()
        result = dict()

        for currency_type in config.CURRENCIES:
            if currency_type == currency_from:
                result[currency_type] = float(amount)
                continue

            if not self._rates.get(currency_type, None) \
                    or not self._rates.get(currency_from, None):
                result[currency_type] = NO_RATES
                logger.info("Попробуем загрузить курсы еще раз")
                await self.prepare_rates(force=True)
            else:
                result[currency_type] = round(
                    (
                        float(amount) *
                        self._rates[currency_from] /
                        self._rates[currency_type]
                    ),
                    2
                )

        return result
