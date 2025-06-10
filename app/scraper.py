import requests
from bs4 import BeautifulSoup
from app.db import SessionLocal
from app.models import Car
from sqlalchemy.exc import IntegrityError
from app.config import START_URL
import re
import time
from random import uniform
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def create_session():
    session = requests.Session()

    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )

    adapter = HTTPAdapter(
        max_retries=retries,
        pool_connections=10,
        pool_maxsize=10
    )
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session


def parse_odometer(text):
    if not text:
        return 0
    text = text.lower().replace("тис.", "").replace("км", "").strip()
    try:
        return int(float(text.replace(',', '.')) * 1000)
    except:
        return 0


def parse_car(url, db_session, request_session):
    try:
        time.sleep(uniform(0.5, 2))

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = request_session.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find("h1").text.strip() if soup.find("h1") else "No title"

        price_elem = soup.select_one(".price_value")
        price = int(re.sub(r"\D", "", price_elem.text)) if price_elem else 0

        odometer_elem = soup.select_one(".base-information span:-soup-contains('Пробіг')")
        odometer = parse_odometer(odometer_elem.text) if odometer_elem else 0

        username_elem = soup.select_one(".seller_info_name")
        username = username_elem.text.strip() if username_elem else "No username"

        phone_number = "+380..."  # Default value

        image_elem = soup.select_one(".photo-620x465")
        image_url = image_elem["src"] if image_elem else ""

        images_count = len(soup.select(".photo-620x465")) if soup.select(".photo-620x465") else 0

        car_number_elem = soup.find(text=re.compile("Номер"))
        car_number = car_number_elem.find_next().text if car_number_elem else ""

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

        db_session.add(car)
        db_session.commit()

    except IntegrityError:
        db_session.rollback()
    except Exception as e:
        print(f"Error parsing {url}: {str(e)}")
        db_session.rollback()


def scrape():
    db_session = SessionLocal()
    request_session = create_session()

    request_session.timeout = 10

    print("Scraping started...")
    page = 0
    max_pages = 10

    while page < max_pages:
        try:
            page_url = f"{START_URL}?page={page}"
            print(f"Processing page {page}")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = request_session.get(page_url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            links = [a["href"] for a in soup.select(".ticket-title a") if "auto" in a["href"]]

            if not links:
                break

            for link in links:
                parse_car(link, db_session, request_session)

            page += 1
            time.sleep(uniform(1, 3))

        except Exception as e:
            print(f"Error processing page {page}: {str(e)}")
            break

    db_session.close()
    request_session.close()
    print("Scraping finished.")