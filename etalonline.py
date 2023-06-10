import asyncio
import logging
from typing import List, Optional

import aiohttp
from bs4 import BeautifulSoup, Tag

import config

logger = logging.getLogger(__name__)


async def download_rates() -> Optional[dict]:
    logger.info("Загружаем валюты.")
    new_rates = dict()

    try:
        html = await _get_etalononline_page()
        data = _extract_rates_table(html)
        data = _remove_short_rows(data)

        # Let's hardcode title and rates location
        title: list = _fix_euro(data[1])
        rates: list = data[2]

        for currency_type in config.CURRENCIES:
            if currency_type == config.BYN:
                new_rates[currency_type] = 1
            else:
                currency_index = title.index(currency_type)
                currency_value = float(rates[currency_index])
                new_rates[currency_type] = currency_value

        logger.info("Загрузили.")
        return new_rates
    except Exception:
        logger.exception("Error while loading exchange rates")
        return None


def _fix_euro(currencies: list) -> list:
    cursed_eur = "ЕUR"
    blessed_eur = "EUR"
    index = currencies.index(cursed_eur)
    currencies[index] = blessed_eur
    return currencies


def _extract_rates_table(html: str) -> List[list]:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", attrs={"id": "val"})

    if not table:
        raise Exception("Can't find rates 1")

    table_body: Tag = table.find("tbody")  # type: ignore

    if not table_body:
        raise Exception("Can't find rates 2")

    data = []
    rows = table_body.find_all("tr")

    for row in rows:
        cols = row.find_all("td")
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


async def _get_etalononline_page() -> str:
    url = "https://etalonline.by/spravochnaya-informatsiya/valuta/"

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
