import aiopg
import asyncio
from settings import settings

dsn = "host={} port={} dbname={} user={} password={}".format(
    settings.DB_HOST, settings.DB_PORT, settings.DB_NAME, settings.DB_USER, settings.DB_PASSWORD
)

intsys_status_query = """
    DROP TABLE IF EXISTS intsys_status;
    CREATE TABLE intsys_status (
        id SERIAL,
        result VARCHAR(512) NOT NULL
    );
"""

carrier_status_query = """
    DROP TABLE IF EXISTS carrier_status;
    CREATE TABLE carrier_status (
        id SERIAL PRIMARY KEY,
        result VARCHAR(512) NOT NULL
    );
"""

carrier_message_query = """
    DROP TABLE IF EXISTS carrier_message;
    CREATE TABLE carrier_message (
        id SERIAL PRIMARY KEY,
        message VARCHAR(512) NOT NULL
    );
"""

settings_query = """
    DROP TABLE IF EXISTS settings;
    CREATE TABLE settings (
        id SERIAL PRIMARY KEY,
        name VARCHAR(128) UNIQUE NOT NULL, 
        value VARCHAR(256)
    );
"""

async def run_migration():
    pool = await aiopg.create_pool(dsn)
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(intsys_status_query)
            await cursor.execute(carrier_status_query)
            await cursor.execute(carrier_message_query)
            await cursor.execute(settings_query)
            conn.commit()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    task = loop.create_task(run_migration())
    loop.run_until_complete(task)