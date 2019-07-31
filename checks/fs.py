from urllib.parse import urljoin

import aiohttp

from checks import _get_kafka_messages, Check
from aiologger import Logger

logger = Logger.with_default_handlers()


async def get_fs_messages(start):
    return await _get_kafka_messages('fs', start)


class FSKafkaCheck:
    async def check(self, fs_messages):
        logger.info("[FS-Kafka] checking...")
        logger.info(f"[FS-Kafka] messages: {fs_messages}")
        result = any(fs_messages)
        logger.info(f"[FS-Kafka] check: {result}")
        return result


class FSCheck:
    def __init__(self, server_url, token, fact_type, fact_result) -> None:
        super().__init__()
        self.server_url = server_url
        self.token = token
        self.fact_type = fact_type
        self.fact_result = fact_result

    async def _get_facts(self, fs_messages):
        result = []
        headers = {'Authorization': f'Token {self.token}'}
        async with aiohttp.ClientSession(headers=headers) as session:
            for message in fs_messages:
                fact_id = message.value["id"]["fact"]["uuid"]
                url = urljoin(self.server_url, f'/api/v1/facts/{fact_id}')
                logger.info(f"[FS] trying to get facts: {url}")
                async with session.get(url) as resp:
                    logger.info(f"[FS] response: {resp.status }")
                    if resp.status == 200:
                        result.append(await resp.json())
        return result

    async def check(self, fs_messages):
        logger.info("[FS] checking...")
        facts = await self._get_facts(fs_messages)
        logger.info(f"[FS] got facts. {len(facts)}")
        for fact in facts:
            logger.info(f"[FS] Checking fact: {fact}")
            if fact['type'] == self.fact_type:
                if 'link' in fact['result']:
                    if fact['result']["link"].split('/')[-1] == self.fact_result:
                        logger.info(f"[FS] Link Check TRUE")
                        return True
                else:
                    if fact['result'] == self.fact_result:
                        logger.info(f"[FS] Whole res Check TRUE")
                        return True

        logger.info(f"[FS] Check FALSE")
        return False
