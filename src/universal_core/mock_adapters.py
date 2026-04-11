import os
import asyncio
from typing import Dict, Any, Type, List
from pydantic import BaseModel

from src.universal_core.interfaces import (
    BaseStateStore,
    BaseMessageBroker,
    BaseVectorStore,
    BaseFileStorage,
    BaseTelemetry,
    BaseMCPServer,
    AgentContext
)

class MockStateStore(BaseStateStore):
    def __init__(self, config=None):
        self.config = config
        self._store: Dict[str, dict] = {}

    async def save_state(self, key: str, state: BaseModel) -> None:
        self._store[key] = state.model_dump()

    async def load_state(self, key: str, state_model: Type[BaseModel]) -> BaseModel:
        data = self._store.get(key, {})
        return state_model(**data)

class MockMessageBroker(BaseMessageBroker):
    def __init__(self, config=None):
        self.config = config
        self._queues: Dict[str, asyncio.Queue] = {}

    def _get_queue(self, queue_name: str) -> asyncio.Queue:
        if queue_name not in self._queues:
            self._queues[queue_name] = asyncio.Queue()
        return self._queues[queue_name]

    async def publish(self, queue_name: str, payload: BaseModel, context: AgentContext) -> None:
        q = self._get_queue(queue_name)
        await q.put({
            "payload": payload.model_dump(),
            "context": context.model_dump()
        })

    async def listen(self, queue_name: str) -> Any:
        q = self._get_queue(queue_name)
        return await q.get()

class MockVectorStore(BaseVectorStore):
    def __init__(self, config=None):
        self.config = config

    async def semantic_search(self, query: str, limit: int = 5) -> List[BaseModel]:
        return []

class MockFileStorage(BaseFileStorage):
    def __init__(self, config=None):
        self.config = config
        self._files: Dict[str, bytes] = {}

    async def save_file(self, filename: str, content: bytes) -> str:
        file_id = f"mock_{filename}"
        self._files[file_id] = content
        return file_id

    async def get_file(self, file_id: str) -> bytes:
        if file_id not in self._files:
            raise FileNotFoundError(f"File {file_id} not found in mock storage.")
        return self._files[file_id]

class MockTelemetry(BaseTelemetry):
    def __init__(self, config=None):
        self.config = config

    def record_metric(self, name: str, value: float, tags: dict) -> None:
        pass

class MockMCPServer(BaseMCPServer):
    def __init__(self, config=None):
        self.config = config

    async def start_sse_stream(self) -> Any:
        async def mock_stream():
            yield "data: mock_sse_started\n\n"
        return mock_stream()

    def register_tools(self, tools: list) -> None:
        pass
