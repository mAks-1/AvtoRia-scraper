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


