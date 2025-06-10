import aiohttp
from bs4 import BeautifulSoup
from app.db import get_session
from app.models import Car
from app.config import START_URL
from sqlalchemy.exc import IntegrityError
import asyncio
import re
from random import uniform


async def fetch(session, url):
    await asyncio.sleep(uniform(0.5, 2))
    headers = {'User-Agent': 'Mozilla/5.0 ...'}
    async with session.get(url, headers=headers) as response:
        response.raise_for_status()
        return await response.text()


def parse_odometer(text):
    if not text:
        return 0
    text = text.lower().replace("тис.", "").replace("км", "").strip()
    try:
        if 'тис' in text:
            numeric_part = re.sub(r'[^0-9,.]', '', text)
            return int(float(numeric_part.replace(',', '.')) * 1000)
        else:
            numeric_part = re.sub(r'[^0-9]', '', text)
            return int(numeric_part)
    except Exception:
        return 0


async def parse_car(url, http_session):
    db = await get_session()
    try:
        html = await fetch(http_session, url)
        soup = BeautifulSoup(html, "html.parser")

        title = soup.find("h1").text.strip() if soup.find("h1") else "No title"
        price_elem = soup.select_one(".price_value")
        price = int(re.sub(r"\D", "", price_elem.text)) if price_elem else 0

        odometer = 0
        odometer_text = soup.select_one(".technical-info > dd")
        if odometer_text and "пробіг" in odometer_text.get_text().lower():
            odometer = parse_odometer(odometer_text.get_text())
        else:
            odometer_elem = soup.select_one(".base-information span:-soup-contains('Пробіг')")
            odometer = parse_odometer(odometer_elem.text) if odometer_elem else 0

        username = soup.select_one(".seller_info_name").text.strip() if soup.select_one(
            ".seller_info_name") else "No username"

        phone_number = "+380..."

        image_elem = soup.select_one(".photo-620x465")
        image_url = image_elem["src"] if image_elem and "src" in image_elem.attrs else ""
        images_count = len(soup.select(".photo-620x465"))

        car_number = ""
        car_vin = ""

        info_blocks = soup.select(".technical-info-list li")
        for block in info_blocks:
            text = block.get_text()
            if "Номер" in text:
                car_number = block.select_one(".label").text.strip() if block.select_one(
                    ".label") else ""
            elif "VIN" in text:
                car_vin = block.select_one(".label").text.strip() if block.select_one(
                    ".label") else ""

        if not car_number:
            car_number_elem = soup.find(text=re.compile("Номер"))
            car_number = car_number_elem.find_next().text if car_number_elem else ""
        if not car_vin:
            car_vin_elem = soup.find(text=re.compile("VIN"))
            car_vin = car_vin_elem.find_next().text if car_vin_elem else ""

        car = Car(
            url=url,
            title=title,
            price_usd=price,
            odometer=odometer,
            username=username,
            phone_number=phone_number,
            image_url=image_url,
            images_count=images_count,
            car_number=car_number,
            car_vin=car_vin
        )
        db.add(car)
        await db.commit()
        print(f"[SCRAPED] {url}")

    except IntegrityError:
        await db.rollback()
        print(f"[DUPLICATE] {url}")
    except Exception as e:
        print(f"[ERROR] {url} — {e}")
        await db.rollback()
    finally:
        await db.close()


async def scrape():
    from app.config import MAX_PAGES
    async with aiohttp.ClientSession() as session:
        print("Scraping started...")
        for page in range(MAX_PAGES):
            try:
                page_url = f"{START_URL}?page={page}"
                html = await fetch(session, page_url)
                soup = BeautifulSoup(html, "html.parser")
                links = [a["href"] for a in soup.select(".ticket-title a") if "auto" in a["href"]]
                if not links:
                    print(f"No links found on page {page}, stopping.")
                    break

                await asyncio.gather(*[parse_car(link, session) for link in links])

                await asyncio.sleep(uniform(1, 3))
            except Exception as e:
                print(f"[PAGE ERROR] {page} — {e}")
                break

    print("Scraping finished.")