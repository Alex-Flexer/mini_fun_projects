from requests import get
from bs4 import BeautifulSoup
from googletrans import Translator
from transliterate import translit
import asyncio


translator = Translator()


async def translator_translate(word):
    result = await translator.translate(word, dest='en')
    return result.text


def get_temperature(city: str):
    headers = {"Cookie": 'yw_allergy_promo=1; _yasc=C/lSJLsx+LcIFqJEVJ5alUTH0LzCggmYJPuJnUO46jIusznQHntlJ8EOl8v7nLRSYYmAlQ8=; i=X0wHJMzYf0z2cQ8IWvoE0YLjpL6PJbVmy6fwOV0YEihHD2JYSS9tyTQWKE8Kq/oVyeZmqw9XM+Mcnng/aS/+Q0Wc0Rg=; yandexuid=4308001361737620354; yashr=9853474291737620354; bh=YIrR2cAGahLcyumIDvKso64E5cjwjgOUtgI=; is_gdpr=0; is_gdpr_b=CKKpXBD6twIoAg==; receive-cookie-deprecation=1; yuidss=4308001361737620354; yp=2058016242.multib.1#2058016310.udn.cDpzYXNoYWZsZXhzZXI%3D; yandex_login=sashaflexser; maps_routes_travel_mode=masstransit; Session_id=3:1745780859.5.0.1742656310235:vOmMsg:6697.1.2:1|973718500.-1.2.3:1742656310|3:10306641.448704.be7Wt_j_R7vFM8qsDExnrwhh-AI; sessar=1.1201.CiBZn0af6EvXv22ez8a5SV0EwrIxz7LOkrExTuj0sUJ9jA.F_DfrOD2TzV82SS4oA1VDJO24d2_fXjNBJfdQrDNjVc; sessionid2=3:1745780859.5.0.1742656310235:vOmMsg:6697.1.2:1|973718500.-1.2.3:1742656310|3:10306641.448704.fakesign0000000000000000000; skid=6127090731743349570; KIykI=1; coockoos=6'}
    resp = get(f"https://yandex.ru/pogoda/ru/{city}", headers=headers)
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
