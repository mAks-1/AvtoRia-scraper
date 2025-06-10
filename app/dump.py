import os
import subprocess
import datetime
from app.db import get_session
from app.config import DATABASE_URL


async def dump_db():
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
    print(f"[DUMPER] Database dumped to {filename}")