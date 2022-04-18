import asyncio
import logging
from typing import List, Optional

import aiohttp
from bs4 import BeautifulSoup

import config

logger = logging.getLogger(__name__)


async def download_rates() -> Optional[dict]:
    logger.info('Загружаем валюты.')
    new_rates = dict()
    new_rates[config.BYN] = 1

    try:
        html = await _get_page()
        data = _extract_rates_table(html)
        data = _remove_short_rows(data)

        for row in data:
            currancy_name: str = row[2].upper()

            if currancy_name in config.CURRENCIES:
                currency_amount_len = len(row[1])
                currency_amount = float(row[1].replace(",", "."))
                currency_value = round(
                    float(row[3].replace(",", ".")) / currency_amount,
                    4 + currency_amount_len - 1
                )

                new_rates[currancy_name] = currency_value

        logger.info('Загрузили.')
        return new_rates
    except Exception:
        logger.exception("Error while loading exchange rates")
        return None


def _extract_rates_table(html: str) -> List[list]:
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', attrs={'id': 'table-currencies'})
    table_body = table.find('tbody')
    data = []
    rows = table_body.find_all('tr')

    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        # Get rid of empty values
        data.append([ele for ele in cols if ele])

    return data


def _remove_short_rows(data):
    length = _get_median_length(data)
    new_data = list()

    for row in data:
        if len(row) == length:
            new_data.append(row)

    return new_data


def _get_median_length(data):
    lengths = {}

    for row in data:
        length = len(row)
        lengths[length] = lengths.get(length, 0) + 1

    median_length = 0
    rate = 0

    for length in lengths:
        if lengths[length] > rate:
            rate = lengths[length]
            median_length = length

    return median_length


async def _get_page() -> str:
    url = "https://select.by/kursy-valyut/natsbank-rb"

    try:
        async with aiohttp.ClientSession() as http_session:
            async with http_session.get(url) as response:
                if response.status != 200:
                    return ""

                return await response.text()

    except Exception:
        logger.exception(f"Error while downloading page: {url}")
        return ""

if __name__ == "__main__":
    asyncio.run(download_rates())
