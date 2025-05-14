from requests import get
import asyncio
from dotenv import dotenv_values
import re

from bs4 import BeautifulSoup
from googletrans import Translator
from transliterate import translit


translator = Translator()

def parse_cookies(cookie_string: str) -> dict:
    return {match.group(1): match.group(2) for match in (re.match(r'^([^=]+)=(.*)$', pair) for pair in cookie_string.split('; ')) if match}

config = dotenv_values(".env")
YANDEX_COOKIES = parse_cookies(config["COOKIES"])


async def translator_translate(word):
    result = await translator.translate(word, dest='en')
    return result.text


def get_temperature(city: str):
    resp = get(f"https://yandex.ru/pogoda/ru/{city}", cookies=YANDEX_COOKIES)
    res = None
    if resp.ok:
        bs = BeautifulSoup(resp.text, "html.parser")
        temperature_el = bs.select_one(".AppFactTemperature_wrap__z_f_O")
        if temperature_el is not None:
            res = temperature_el.text.replace("°", "")
    return res

async def main():
    input_city = input()
    translate_city = (await translator_translate(input_city)).lower().replace(" ", "-")
    translite_city = translit(input_city, "ru", reversed=True).lower()
    res = get_temperature(translate_city)
    if not res:
        res = get_temperature(translite_city)
    print(res)

asyncio.run(main())
