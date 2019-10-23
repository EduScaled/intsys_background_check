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

from aiologger import Logger

from checks.carrier import CarrierCheck
from checks.dp import DPCheck
from checks.fs import FSKafkaCheck, get_fs_messages, FSCheck
from checks.lrs import LrsKafkaCheck, LrsResponseCheck, create_lrs
from clean_up import clean_up_services, get_clean_up_settings
from settings import settings

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.SENTRY_ENVIRONMENT,
    integrations=[AioHttpIntegration()]
)

dsn = "host={} port={} dbname={} user={} password={}".format(
    settings.DB_HOST, settings.DB_PORT, settings.DB_NAME, settings.DB_USER, settings.DB_PASSWORD
)


logger = Logger.with_default_handlers()


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


async def process_carrier_check():
    result = await run_check(
        CarrierCheck(settings.CARRIER_SERVER_URL, settings.CARRIER_SERVER_TOKEN).check)
    return {
        'carrier-kafka-write': result,
        'status': 200 if result else 500,
        "created_at": str(datetime.datetime.utcnow())
    }


async def save_result(result, table):
    select_query = "SELECT result FROM {};".format(table)
    
    insert_query = """
        DELETE FROM {table};
        INSERT INTO {table} (result) VALUES ('{value}');
    """.format(table=table, value=json.dumps(result))

    update_query = "UPDATE {} SET result = '{}';".format(table, json.dumps(result))

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


async def intsys_clean_up():
    while True:
        if not await check_is_enabled():
            await asyncio.sleep(2)
            continue

        cleanup_settings = await get_clean_up_settings()
        if not cleanup_settings:
            logger.info(f"(!) Not enough settings to clean up... Sleeping 60s.")
            await asyncio.sleep(60)
            continue

        logger.info("Cleaning up in progress...")
        await clean_up_services(cleanup_settings)

        clean_up_interval = int(cleanup_settings['clean_up_interval'])
        logger.info(f"Cleaning up sleeping {clean_up_interval}s.")
        await asyncio.sleep(clean_up_interval)


async def intsys_check():
    logger.info("Checking process started. Please do not forget to enable checks.")
    while True:
        if not await check_is_enabled():
            await asyncio.sleep(2)
            continue
        logger.info("Checking in progress...")
        result = await process_intsys_check()
        await save_result(result, 'intsys_status')
        result = await process_carrier_check()
        await save_result(result, 'carrier_status')

        logger.info("Checking sleeping 60s.")
        await asyncio.sleep(60)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(intsys_check())
    loop.create_task(intsys_clean_up())
    loop.run_forever()