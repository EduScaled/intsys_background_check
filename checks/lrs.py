import asyncio
from asyncio import ensure_future
from urllib.parse import urljoin

import aiohttp

from aiologger import Logger
from checks import _get_kafka_messages
from utils import send_request

loop = asyncio.get_event_loop()

logger = Logger.with_default_handlers()

async def create_lrs(server_url, auth, unti_id, culture_value):
    headers = {
        'Authorization': f'Basic {auth}',
        'X-Experience-API-Version': '1.0.3',
    }

    message = {
        "actor": {
            "objectType": "Agent",
            "account": {
                "homePage": "https://my.2035.university/",
                "name": unti_id
            }
        },
        "verb": {
            "id": "https://my.2035.university/xapi/v1/verbs/finished"
        },
        "object": {
            "id": "https://my.2035.university/xapi/v1/activity/culturegame",
            "definition": {
                "name": {
                    "ru": "Игра: организационная культура"
                }
            },
            "objectType": "Activity"
        },
        "result": {
            "success": True,
            "completion": True,
            "extensions": {
                "https://my.2035.university/xapi/v1/results/culture": culture_value
            }
        },
        "timestamp": "2018-12-27T17:27:18.528Z",
        "stored": "2018-12-27T17:27:18.528Z",
        "authority": {
            "objectType": "Agent",
            "name": "culturegame",
            "mbox": "mailto:hello@learninglocker.net"
        },
        "version": "1.0.0"
    }

    url = urljoin(server_url, '/data/xAPI/statements')
    response, status = await ensure_future(send_request(url, headers, message))

    logger.info(f"LRS response: {response} {status}")
    return response, status


class LrsResponseCheck:
    async def check(self, lrs_response, lrs_response_status):
        return lrs_response_status == 200 \
               and isinstance(lrs_response, list) \
               and len(lrs_response) == 1


class LrsKafkaCheck:
    @classmethod
    def _get_lrs_ids_from_messages(cls, messages):
        for message in messages:
            try:
                yield message.value['id']['id']
            except KeyError:
                pass

    async def check(self, start, lrs_response):
        messages = await _get_kafka_messages('lrs', start=start)
        lrs_id = lrs_response[0]
        return lrs_id in set(self._get_lrs_ids_from_messages(messages))
