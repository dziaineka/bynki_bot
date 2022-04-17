import asyncio
import logging
from datetime import datetime, timedelta
import nbrb

import config

NO_RATES = '🤷‍♀️ Не удалось получить курс НБРБ'
logger = logging.getLogger(__name__)


class Exchanger:
    def __init__(self):
        self._rates = dict()
        self._rates_expiration = datetime.utcnow()
        self._downloading_in_progress = False
        self.download_rates_function = nbrb.download_rates

    def _set_expiration_time(self):
        next_day = datetime.utcnow() + timedelta(days=1)
        self._rates_expiration = datetime(next_day.year,
                                          next_day.month,
                                          next_day.day, 9, 0, 0)

    async def exchange(self, amount: float, currency_from: str) -> dict:
        await self.download_rates()
        result = dict()

        for currency_type in config.CURRENCIES:
            if currency_type == currency_from:
                result[currency_type] = float(amount)
                continue

            if not self._rates.get(currency_type, None) \
                    or not self._rates.get(currency_from, None):
                result[currency_type] = NO_RATES
                logger.info("Попробуем загрузить курсы еще раз")
                asyncio.create_task(self.download_rates(force=True))
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

    async def download_rates(self, force=False):
        if self._rates_expiration > datetime.utcnow() and not force:
            return

        if self._downloading_in_progress:
            logger.info("Уже загружаются")
            return

        self._downloading_in_progress = True
        result = await self.download_rates_function()

        if result:
            self._rates = result

        self._set_expiration_time()
        self._downloading_in_progress = False
