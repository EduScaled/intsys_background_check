import uuid
from urllib.parse import urljoin

import aiohttp
import aiopg

from settings import settings

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


    async def check(self):
        headers = {'Authorization': f'{self.token}'}
        message = uuid.uuid4().hex
        async with aiohttp.ClientSession(headers=headers) as session:
            url = urljoin(self.server_url, '/produce/')
            body = {
                "topic": self.topic,
                "payload": str(message)
            }
            await self.write_sent_message_to_db(message)
            async with session.post(url, json=body) as resp:
                if resp.status == 200:
                    return True
                else:
                    return False
