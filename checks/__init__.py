import ast
import asyncio
import json
from json import JSONDecodeError
from typing import List

from aiologger import Logger
from aiokafka import AIOKafkaConsumer, ConsumerRecord
from kafka import TopicPartition

from settings import settings

logger = Logger.with_default_handlers()


class Check:
    async def check(self, **kwargs):
        raise NotImplementedError()


async def _get_kafka_messages(topic: str, start: int) -> List[ConsumerRecord]:
    def _value_deserializer(value):
        value = value.decode("utf-8")
        try:
            return json.loads(value)
        except JSONDecodeError:
            return ast.literal_eval(value)

    loop = asyncio.get_event_loop()
    consumer = AIOKafkaConsumer(
        topic, value_deserializer=_value_deserializer,
        loop=loop, bootstrap_servers=settings.KAFKA_SERVER,
    )

    await consumer.start()
    try:
        partitions = consumer.partitions_for_topic(topic)
        tps = [TopicPartition(topic, p) for p in partitions]

        offsets = await consumer.offsets_for_times({tp: start for tp in tps})
        for tp, offset in offsets.items():
            offset = offset.offset if offset else (await consumer.end_offsets([tp]))[tp]
            consumer.seek(tp, offset)

        records = await consumer.getmany(*tps, timeout_ms=1000*60)

        messages = []
        for tp in tps:
            messages += records.get(tp, [])
        logger.info(f"Got kafka messages {messages} by key {topic}")
        return messages
    finally:
        # Will leave consumer group; perform autocommit if enabled.
        await consumer.stop()

