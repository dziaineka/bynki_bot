import aiohttp
import config
import json


class Exchanger:
    def __init__(self):
        self._timeout = aiohttp.ClientTimeout(connect=5)
        self._http_session = aiohttp.ClientSession()
        self._rates = dict()

    def __del__(self):
        self._http_session.close()

    async def _get_rate(self, currency_type):
        if currency_type == config.BYN:
            return 1

        url = 'http://www.nbrb.by/API/ExRates/Rates/' + currency_type + '?'

        params = {
            'ParamMode': 2
        }

        try:
            async with self._http_session.get(
                                url,
                                params=params,
                                timeout=self._timeout) as response:
                if response.status != 200:
                    return None

                resp_json = await response.json(content_type=None)
                return resp_json['Cur_OfficialRate'] / resp_json['Cur_Scale']

        except aiohttp.client_exceptions.ServerTimeoutError:
            return None

        except json.decoder.JSONDecodeError:
            return None

        except IndexError:
            return None

    async def download_currencies(self):
        for currency_type in config.CURRENCIES:
            self._rates[currency_type] = await self._get_rate(currency_type)

    def exchange(self, amount, currency_from):
        result = dict()

        for currency_type in config.CURRENCIES:
            if not self._rates[currency_type]:
                result[currency_type] = '🤷‍♀️'
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
