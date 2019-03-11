from urllib.parse import urljoin

import aiohttp

from checks import _get_kafka_messages, Check


async def get_fs_messages(start):
    return await _get_kafka_messages('fs', start)


class FSKafkaCheck:
    async def check(self, fs_messages):
        return any(fs_messages)


class FSCheck:
    def __init__(self, server_url, token, fact_result) -> None:
        super().__init__()
        self.server_url = server_url
        self.token = token
        self.fact_result = fact_result

    async def _get_facts(self, fs_messages):
        result = []
        headers = {'Authorization': f'Token {self.token}'}
        async with aiohttp.ClientSession(headers=headers) as session:
            for message in fs_messages:
                fact_id = message.value["id"]["fact"]["uuid"]
                url = urljoin(self.server_url, f'/api/v1/facts/{fact_id}')
                async with session.get(url) as resp:
                    if resp.status == 200:
                        result.append(await resp.json())
        return result

    async def check(self, fs_messages):
        facts = await self._get_facts(fs_messages)
        for fact in facts:
            if fact['type'] == 'lrs.culture.user.result' and fact['result'] == self.fact_result:
                return True
        return False
