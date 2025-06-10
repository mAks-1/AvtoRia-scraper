import asyncio
from asyncio import Future

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.scraper import scrape
from app.config import SCRAPING_TIME, DUMP_TIME
from app.dump import dump_db


async def start():
    scheduler = AsyncIOScheduler()
    h, m = map(int, SCRAPING_TIME.split(":"))
    scheduler.add_job(scrape, "cron", hour=h, minute=m)

    dh, dm = map(int, DUMP_TIME.split(":"))
    scheduler.add_job(dump_db, "cron", hour=dh, minute=dm)

    scheduler.start()
    print("Scheduler started")

    await Future()


if __name__ == "__main__":
    asyncio.run(start())
