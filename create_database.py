import aiopg
import asyncio

from clean_up import get_default_clean_up_settings_dict
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


def get_default_settings_insert_query():
    result_queries = []
    default_settings = get_default_clean_up_settings_dict()

    template_query = """
        INSERT INTO settings (name, value)
        VALUES ('{parameter_name}', '{value}')
        ON CONFLICT (name)
        DO UPDATE SET
        value='{value}';
        """

    for parameter_name, value in default_settings.items():
        query = template_query.format(parameter_name=parameter_name, value=value)
        result_queries.append(query)

    return "\n".join(result_queries)


async def run_migration():
    pool = await aiopg.create_pool(dsn)
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(intsys_status_query)
            await cursor.execute(carrier_status_query)
            await cursor.execute(carrier_message_query)
            await cursor.execute(settings_query)
            # await cursor.execute(get_default_settings_insert_query())
            conn.commit()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    task = loop.create_task(run_migration())
    loop.run_until_complete(task)