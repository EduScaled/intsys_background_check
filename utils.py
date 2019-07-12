import logging
import aiohttp


async def send_request(url, headers, json_data):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=json_data) as response:
                return await response.json(), response.status
        except (aiohttp.client_exceptions.ClientConnectionError,):
            logging.error(f"(!) Background healhcheck can't make POST to client: {url}",
                         extra={
                             'url': url,
                             'json': json_data
                         })
            return None, 500