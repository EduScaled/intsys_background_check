import uuid
from asyncio import ensure_future
from urllib.parse import urljoin

import aiohttp
import aiopg

from aiologger import Logger
from settings import settings
from utils import send_request

logger = Logger.with_default_handlers()


class CarrierCheck:
    def __init__(self, server_url, token) -> None:
        super().__init__()
        self.server_url = server_url
        self.token = token
        self.topic = 'healthcheck'
        self.dsn = "host={} port={} dbname={} user={} password={}".format(
            settings.DB_HOST, settings.DB_PORT, settings.DB_NAME, settings.DB_USER, settings.DB_PASSWORD
        )

    async def write_sent_message_to_db(self, message):
        select_query = "SELECT message FROM carrier_message;"
        insert_query = """
                DELETE FROM carrier_message;
                INSERT INTO carrier_message (message) VALUES ('{value}');
            """.format(value=message)
        update_query = "UPDATE carrier_message SET message = '{}';".format(message)

        pool = await aiopg.create_pool(self.dsn)
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(select_query)
                query = insert_query if len(await cursor.fetchall()) != 1 else update_query
                await cursor.execute(query)
                conn.commit()
        logger.info(f"[Carrier] Write sent message to db.")

    async def check(self):
        headers = {'Authorization': f'{self.token}'}
        message = uuid.uuid4().hex

        url = urljoin(self.server_url, '/produce/')
        body = {
            "topic": self.topic,
            "payload": str(message)
        }
        await self.write_sent_message_to_db(message)
        logger.info(f"[Carrier] Trying to produce. Url: {url}")

        response, status = await ensure_future(send_request(url, headers, body))
        if status == 200:
            return True
        return False
