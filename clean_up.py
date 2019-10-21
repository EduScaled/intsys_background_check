
from aiologger import Logger
import aiopg

from settings import settings

logger = Logger.with_default_handlers()


def get_default_clean_up_settings_dict():
    return {
        'fh_db_name': 'fh',
        'fh_db_host': '127.0.0.1',
        'fh_db_port': 5532,
        'fh_db_user': 'postgres',
        'fh_db_password': 'postgres',
        'int_db_name': 'int_test',
        'int_db_host': '127.0.0.1',
        'int_db_port': 5533,
        'int_db_user': 'postgres',
        'int_db_password': 'postgres',
        'fs_db_name': 'fs_data',
        'fs_db_host': '127.0.0.1',
        'fs_db_port': 5531,
        'fs_db_user': 'postgres',
        'fs_db_password': 'postgres',
        'cleanup_unti_ids': '1,2,3,4',
        'objects_expiration_time': 10, # minutes
        'clean_up_interval': 60, # seconds
    }


def _is_settings_enough(settings_dict):
    cleanup_settings_count = len(get_default_clean_up_settings_dict())
    if len(settings_dict) >= cleanup_settings_count:
        return True

    return False


async def get_clean_up_settings():
    result = {}
    dsn = "host={} port={} dbname={} user={} password={}".format(
    settings.DB_HOST, settings.DB_PORT, settings.DB_NAME, settings.DB_USER, settings.DB_PASSWORD)
    pool = await aiopg.create_pool(dsn)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id, name, value FROM settings")
            async for id, name, value in cur:
                if 'fs_' in name or 'int_' in name or 'fh_' in name or\
                        'clean_up_interval' in name or 'objects_expiration_time' in name or 'cleanup_unti_ids' in name:
                    result[name] = value
            logger.info("Got clean up settings.")
            if _is_settings_enough(result):
                return result
    return {}


async def clean_up(service_name, query, cleanup_settings):
    cleanup_unti_ids = cleanup_settings['cleanup_unti_ids'].split(',')
    objects_expiration_time = cleanup_settings['objects_expiration_time']
    dsn = "host={} port={} dbname={} user={} password={}".format(
        cleanup_settings[f'{service_name}_db_host'], cleanup_settings[f'{service_name}_db_port'],
        cleanup_settings[f'{service_name}_db_name'], cleanup_settings[f'{service_name}_db_user'],
        cleanup_settings[f'{service_name}_db_password'])
    pool = await aiopg.create_pool(dsn)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            for unti_id in cleanup_unti_ids:
                final_query = query.format(unti_id=unti_id, minutes=objects_expiration_time)
                logger.info(f"Executing: {final_query}")
                await cur.execute(final_query)
                conn.commit()


async def clean_up_fs(cleanup_settings):
    fs_query = "DELETE FROM storage_fact WHERE {unti_id} = ANY(actor) AND created_at > now()-'{minutes} minute'::interval;"
    await clean_up('fs', fs_query, cleanup_settings)


async def clean_up_fh(cleanup_settings):
    fh_query = '''DELETE FROM handlers_handlertasklaunch
                WHERE (payload->'id'->'user_result'->>'id')::int = {unti_id} AND created > now()-'{minutes} minute'::interval;'''
    await clean_up('fh', fh_query, cleanup_settings)


async def clean_up_int(cleanup_settings):
    int_query = '''DELETE FROM core_interpretertasklaunch
                   WHERE (result->'uploaded_competences'->0->>'unti_id')::int = {unti_id} AND created > now()-'{minutes} minute'::interval;'''
    await clean_up('int', int_query, cleanup_settings)


async def clean_up_services(cleanup_settings):
    await clean_up_fs(cleanup_settings)
    await clean_up_fh(cleanup_settings)
    await clean_up_int(cleanup_settings)




