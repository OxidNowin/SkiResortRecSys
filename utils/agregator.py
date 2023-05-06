from aiohttp import ClientSession
from bs4 import BeautifulSoup
import json


async def get_tour(adults, nights, start_date, star):
    async with ClientSession() as session:
        url = f"https://tour.checkintime.ru/explore/Moscow-Russia/Ski_resorts?" \
              f"adults={adults}&nights={nights}&start_date={start_date}...{start_date}" \
              f"&sort_by=price,asc&filter_stars={star}"
        async with session.get(url=url) as response:
            r_data = await response.text()
    print(url)
    soup = BeautifulSoup(r_data, "html.parser")
    try:
        data = json.loads(str(soup.find_all('script', {"data-hypernova-key": "SeoApp"})[0]).split('--')[1])['hotels'][0]
    except IndexError:
        return False
    return data
