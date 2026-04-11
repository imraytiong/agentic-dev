import importlib
import logging
from typing import Dict, Any, Optional

# Assuming google_adk provides LlmAgent. Adjust import if needed based on actual adk module.
try:
    from google_adk import LlmAgent
except ImportError:
    # Fallback/Mock for LlmAgent if google_adk is not fully installed or has a different path
    class LlmAgent:
        def __init__(self, **kwargs):
            pass

from .interfaces import (
    BaseStateStore,
    BaseVectorStore,
    BaseFileStorage,
    BaseMessageBroker,
    BaseTelemetry,
    BaseMCPServer
)

logger = logging.getLogger(__name__)

def _deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge dict2 into dict1."""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    return result

class BaseAgentChassis:
    """
    The Universal Orchestration Engine.
    Dynamically loads environment-specific infrastructure via Inversion of Control.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Chassis. 
        `config` should be the merged configuration (e.g., fleet.yaml + config.yaml).
        """
        self.config = config
        self.infrastructure_config = self.config.get("infrastructure", {})
        
        # 1. Instantiate the ADK LlmAgent
        agent_config = self.config.get("agent", {})
        self.llm_agent = LlmAgent(**agent_config)

        # 2. Dynamically load infrastructure adapters
        self.state_store: Optional[BaseStateStore] = self._load_adapter(
            "state_store", BaseStateStore
        )
        self.vector_store: Optional[BaseVectorStore] = self._load_adapter(
            "vector_store", BaseVectorStore
        )
        self.file_storage: Optional[BaseFileStorage] = self._load_adapter(
            "file_storage", BaseFileStorage
        )
        self.message_broker: Optional[BaseMessageBroker] = self._load_adapter(
            "message_broker", BaseMessageBroker
        )
        self.telemetry: Optional[BaseTelemetry] = self._load_adapter(
            "telemetry", BaseTelemetry
        )
        self.mcp_server: Optional[BaseMCPServer] = self._load_adapter(
            "mcp_server", BaseMCPServer
        )

        logger.info("BaseAgentChassis initialized with dynamic infrastructure.")

    def _load_adapter(self, config_key: str, expected_type: type) -> Any:
        """
        Dynamically imports and instantiates an adapter class from a string path.
        Enforces that the loaded class implements the expected Interface (ABC).
        """
        plugin_path = self.infrastructure_config.get(config_key)
        if not plugin_path:
            logger.debug(f"No infrastructure configured for: {config_key}")
            return None

        try:
            module_path, class_name = plugin_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            adapter_class = getattr(module, class_name)
            
            if not issubclass(adapter_class, expected_type):
                raise TypeError(
                    f"Adapter '{plugin_path}' does not implement the expected "
                    f"interface '{expected_type.__name__}'."
                )
            
            # Instantiate and return the adapter
            return adapter_class()
        
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to load adapter '{plugin_path}': {str(e)}")
            raise e
