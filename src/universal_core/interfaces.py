from abc import ABC, abstractmethod
from typing import Type, List, TypeVar, Optional, Any, Dict
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class AgentContext(BaseModel):
    """
    Standardized context object passed through the agent lifecycle.
    """
    user_id: str
    session_id: str
    tenant_id: str
    reply_to: Optional[str] = None
    metadata: Dict[str, Any] = {}

class BaseStateStore(ABC):
    @abstractmethod
    async def save_state(self, key: str, state: BaseModel) -> None:
        """Persist state to the underlying storage."""
        pass

    @abstractmethod
    async def load_state(self, key: str, state_model: Type[T]) -> T:
        """Load state from the underlying storage and validate against the model."""
        pass

class BaseVectorStore(ABC):
    @abstractmethod
    async def semantic_search(self, query: str, limit: int = 5) -> List[BaseModel]:
        """Perform semantic search against the vector database."""
        pass

class BaseFileStorage(ABC):
    @abstractmethod
    async def save_file(self, filename: str, content: bytes) -> str:
        """Save a file and return its URI or file_id."""
        pass

    @abstractmethod
    async def get_file(self, file_id: str) -> bytes:
        """Retrieve a file's content by its URI or file_id."""
        pass

class BaseMessageBroker(ABC):
    @abstractmethod
    async def publish(self, queue_name: str, payload: BaseModel, context: AgentContext) -> None:
        """Publish a message to a queue."""
        pass

    @abstractmethod
    async def listen(self, queue_name: str) -> Any:
        """Listen for messages on a queue."""
        pass

class BaseTelemetry(ABC):
    @abstractmethod
    def record_metric(self, name: str, value: float, tags: dict) -> None:
        """Record a telemetry metric."""
        pass

class BaseMCPServer(ABC):
    @abstractmethod
    async def start_sse_stream(self) -> Any:
        """Start the MCP SSE stream."""
        pass

    @abstractmethod
    def register_tools(self, tools: list) -> None:
        """Register tools with the MCP Server."""
        pass
