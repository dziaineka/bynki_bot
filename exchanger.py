import asyncio
import logging
from datetime import datetime, timedelta
import nbrb
import etalonline
import selectby

import config

NO_RATES = "🤷‍♀️ Не удалось получить курс НБРБ"
logger = logging.getLogger(__name__)


class Exchanger:
    def __init__(self):
        self._rates = dict()
        self._rates_refresh_dt = datetime.utcnow() - timedelta(days=365)
        self._rates_expiration_dt = datetime.utcnow() - timedelta(days=365)
        self._downloading_in_progress = False
        self.download_rates_functions = [
            nbrb.download_rates,
            selectby.download_rates,
            etalonline.download_rates,
        ]

    def _set_refresh_time(self):
        self._rates_refresh_dt = datetime.utcnow() + timedelta(
            hours=config.REFRESH_RATES_INTERVAL
        )

    def _set_expiration_time(self):
        self._rates_expiration_dt = datetime.utcnow() + timedelta(
            hours=config.RATES_TTL
        )

    async def exchange(self, amount: float, currency_from: str) -> dict:
        await self.maybe_update_rates()
        result = dict()

        for currency_type in config.CURRENCIES:
            if currency_type == currency_from:
                result[currency_type] = float(amount)
                continue

            if not self._rates.get(currency_type, None) or not self._rates.get(
                currency_from, None
            ):
                result[currency_type] = NO_RATES
                logger.info("Попробуем загрузить курсы еще раз")
                asyncio.create_task(self.update_rates())
            else:
                result[currency_type] = round(
                    (
                        float(amount)
                        * self._rates[currency_from]
                        / self._rates[currency_type]
                    ),
                    2,
                )

        return result

    async def maybe_update_rates(self):
        now = datetime.utcnow()

        # update rates called when user called conversion, so not to force user
        # to wait for downloading rates we can check if rates is not expired
        # and expose async task to download rates

        if self._rates_refresh_dt > now:
            return

        if self._rates_expiration_dt < now:
            asyncio.create_task(self.update_rates())
            return

        await self.update_rates()

    async def update_rates(self):
        if self._downloading_in_progress:
            logger.info("Уже загружаются")
            return

        self._downloading_in_progress = True

        for download_rates_function in self.download_rates_functions:
            try:
                rates = await asyncio.wait_for(
                    download_rates_function(), timeout=3
                )

                if rates is not None:
                    self._rates = rates
                    self._set_refresh_time()
                    self._set_expiration_time()
                    break
                else:
                    self._rates = dict()
            except asyncio.TimeoutError:
                logger.info("Rates downloading timeout!")

        self._downloading_in_progress = False

    async def wait_first(self, tasks: list):
        done, pending = await asyncio.wait(
            tasks, return_when=asyncio.FIRST_COMPLETED
        )

        for future in pending:
            future.cancel()

        for future in done:
            return future.result()
