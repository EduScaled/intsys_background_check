import aiopg
import asyncio
from settings import settings

dsn = "host={} port={} dbname={} user={} password={}".format(
    settings.DB_HOST, settings.DB_PORT, settings.DB_NAME, settings.DB_USER, settings.DB_PASSWORD
)

query = """
    DROP TABLE IF EXISTS intsys_status;
    CREATE TABLE intsys_status (
        id SERIAL,
        result VARCHAR(512) NOT NULL
    );
"""


async def run_migration():
    pool = await aiopg.create_pool(dsn)
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(query)
            conn.commit()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    task = loop.create_task(run_migration())
    loop.run_until_complete(task)