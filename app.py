import json
import time
import random
import datetime
import asyncio
import aiopg

from typing import Callable

import sentry_sdk
from sentry_sdk import capture_exception
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

from checks.dp import DPCheck
from checks.fs import FSKafkaCheck, get_fs_messages, FSCheck
from checks.lrs import LrsKafkaCheck, LrsResponseCheck, create_lrs
from settings import settings

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.SENTRY_ENVIRONMENT,
    integrations=[AioHttpIntegration()]
)

dsn = "host={} port={} dbname={} user={} password={}".format(
    settings.DB_HOST, settings.DB_PORT, settings.DB_NAME, settings.DB_USER, settings.DB_PASSWORD
)


async def run_check(f: Callable, **kwargs):
    try:
        return await f(**kwargs)
    except Exception as e:
        capture_exception(e)
        return False


async def process_intsys_check():
    
    start = int(time.time() * 1000)
    
    lrs_culture_value = { settings.LRS_CULTURE_COMPETENCE: random.randint(200,300) }

    lrs_response, lrs_response_status = await create_lrs(
        settings.LRS_SERVER_URL, settings.LRS_AUTH, settings.UNTI_ID, lrs_culture_value
    )

    await asyncio.sleep(5)

    fs_messages = await get_fs_messages(start)

    result = {
        'lrs': await run_check(
            LrsResponseCheck().check, lrs_response=lrs_response, lrs_response_status=lrs_response_status
        ),
        'lrs-kafka': await run_check(LrsKafkaCheck().check, start=start, lrs_response=lrs_response),
        'fs': await run_check(
            FSCheck(
                settings.FS_SERVER_URL, settings.FS_SERVER_TOKEN, lrs_culture_value
            ).check, fs_messages=fs_messages
        ),
        'fs-kafka': await run_check(FSKafkaCheck().check, fs_messages=fs_messages),
        'dp:': await run_check(
            DPCheck(
                settings.DP_SERVER_URL, 
                settings.DP_SERVER_TOKEN, 
                settings.UNTI_ID,
                settings.DP_COMPETENCE_UUID,
                lrs_culture_value
            ).check,
            create_entry=settings.DP_CREATE_ENTRY
        )
    }

    status = 200 if all(result.values()) else 500
    result["status"] = status
    result["created_at"] = str(datetime.datetime.utcnow()) 

    return result


async def save_result(result):
    select_query = "SELECT result FROM intsys_status;"
    
    insert_query = """
        DELETE FROM intsys_status;
        INSERT INTO intsys_status (result) VALUES ('{}');
    """.format(json.dumps(result))

    update_query = "UPDATE intsys_status SET result = '{}';".format(json.dumps(result))

    pool = await aiopg.create_pool(dsn)
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(select_query)
            query = insert_query if len(await cursor.fetchall()) != 1 else update_query
            await cursor.execute(query)
            conn.commit()


async def check_is_enabled():
    pool = await aiopg.create_pool(dsn)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id, name, value FROM settings WHERE name = 'is_enabled'")
            async for id, name, value in cur:
                return True if value == "True" or value == "true" else False
            return False


async def intsys_check():
    while True:
        if not await check_is_enabled():
            await asyncio.sleep(2)
            continue
        result = await process_intsys_check()
        await save_result(result)
        await asyncio.sleep(60)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(intsys_check())
    loop.run_forever()