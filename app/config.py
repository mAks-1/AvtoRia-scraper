import os

DATABASE_URL = os.getenv("DATABASE_URL")
SCRAPING_TIME = os.getenv("SCRAPING_TIME")
DUMP_TIME = os.getenv("DUMP_TIME")
START_URL = os.getenv("START_URL")
MAX_PAGES = int(os.getenv("MAX_PAGES"))
