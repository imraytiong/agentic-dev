import os
import json
import logging
import asyncio
from typing import Any, Optional, Dict
from pydantic import BaseModel
import redis.asyncio as redis
from redis.exceptions import RedisError, ResponseError

from universal_core.interfaces import BaseMessageBroker, AgentContext

logger = logging.getLogger(__name__)

class RedisAdapterError(Exception):
    """Base exception for Redis adapter to avoid leaking redis errors."""
    pass

class RedisAdapter(BaseMessageBroker):
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or f"redis://{os.getenv('REDIS_HOST', 'localhost')}:6379/0"
        self._client: Optional[redis.Redis] = None
        # Used for simple pub/sub, though Streams might be better for queues
        self._pubsub = None

    async def connect(self):
        if not self._client:
            try:
                self._client = redis.from_url(self.connection_string)
                # Ping to verify
                await self._client.ping()
            except RedisError as e:
                raise RedisAdapterError(f"Failed to connect to Redis: {e}")

    async def close(self):
        if self._pubsub:
            await self._pubsub.close()
        if self._client:
            await self._client.aclose()
            self._client = None

    async def publish(self, queue_name: str, payload: BaseModel, context: AgentContext) -> None:
        await self.connect()
        try:
            message_data = {
                "payload": payload.model_dump(),
                "context": context.model_dump()
            }
            # Use Redis Streams (XADD) for durable task queues
            # Using '*' for auto-generated ID
            await self._client.xadd(queue_name, {"message": json.dumps(message_data)})
        except RedisError as e:
            raise RedisAdapterError(f"Redis error publishing message: {e}")
        except Exception as e:
            raise RedisAdapterError(f"Unexpected error publishing message: {e}")

    async def listen(self, queue_name: str, consumer_group: str = "agent_group", consumer_name: str = "agent_consumer", block: int = 1000) -> Any:
        await self.connect()
        
        # Ensure consumer group exists
        try:
            await self._client.xgroup_create(queue_name, consumer_group, id="0", mkstream=True)
        except ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise RedisAdapterError(f"Error creating consumer group: {e}")

        try:
            # Block and wait for a message from the stream
            # '>' means get new messages not delivered to other consumers in group
            messages = await self._client.xreadgroup(
                consumer_group,
                consumer_name,
                {queue_name: ">"},
                count=1,
                block=block # Block for specified milliseconds
            )
            
            if messages:
                stream_name, stream_messages = messages[0]
                message_id, message_data = stream_messages[0]
                
                parsed_data = json.loads(message_data[b'message'].decode('utf-8'))
                
                # Acknowledge the message immediately for simplicity, 
                # but in real robust systems, ACK happens after processing.
                await self._client.xack(queue_name, consumer_group, message_id)
                
                return parsed_data, message_id
            return None
        except RedisError as e:
            raise RedisAdapterError(f"Redis error listening to queue: {e}")
        except Exception as e:
            raise RedisAdapterError(f"Unexpected error listening to queue: {e}")
