from apscheduler.schedulers.blocking import BlockingScheduler
from app.scraper import scrape
from app.config import SCRAPING_TIME, DUMP_TIME
import subprocess
import os
import datetime

def dump_db():
    print("[DUMPER] Dump started...")

    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"dumps/dump_{now}.sql"
    os.makedirs("dumps", exist_ok=True)
    subprocess.call([
        "pg_dump",
        "-U", "postgres",
        "-h", "db",
        "-f", filename,
        "autoria"
    ])
    print(f"Database dumped to {filename}")


def start():
    scheduler = BlockingScheduler()
    hour, minute = map(int, SCRAPING_TIME.split(":"))
    scheduler.add_job(scrape, 'cron', hour=hour, minute=minute)

    dhour, dminute = map(int, DUMP_TIME.split(":"))
    scheduler.add_job(dump_db, 'cron', hour=dhour, minute=dminute)

    print("Scheduler started")
    scheduler.start()


if __name__ == "__main__":
    start()