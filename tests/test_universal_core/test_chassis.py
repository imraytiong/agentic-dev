import pytest
from typing import List, Any
from src.universal_core.chassis import BaseAgentChassis
from src.universal_core.interfaces import BaseStateStore
from pydantic import BaseModel

class DummyStateStore(BaseStateStore):
    async def save_state(self, key: str, state: BaseModel) -> None:
        pass

    async def load_state(self, key: str, state_model: type) -> BaseModel:
        return state_model()

class DummyWrongAdapter:
    pass

def test_chassis_initialization_no_adapters():
    config = {
        "infrastructure": {}
    }
    chassis = BaseAgentChassis(config)
    
    assert chassis.state_store is None
    assert chassis.vector_store is None

def test_chassis_loads_valid_adapter(monkeypatch):
    # We will mock importlib so it returns our DummyStateStore
    import importlib
    
    def mock_import_module(name):
        class MockModule:
            DummyStateStore = globals()['DummyStateStore']
        return MockModule()
        
    monkeypatch.setattr(importlib, 'import_module', mock_import_module)
    
    config = {
        "infrastructure": {
            "state_store": "mock_module.DummyStateStore"
        }
    }
    
    chassis = BaseAgentChassis(config)
    assert isinstance(chassis.state_store, DummyStateStore)

def test_chassis_rejects_invalid_adapter(monkeypatch):
    import importlib
    
    def mock_import_module(name):
        class MockModule:
            DummyWrongAdapter = globals()['DummyWrongAdapter']
        return MockModule()
        
    monkeypatch.setattr(importlib, 'import_module', mock_import_module)
    
    config = {
        "infrastructure": {
            "state_store": "mock_module.DummyWrongAdapter"
        }
    }
    
    with pytest.raises(TypeError) as exc_info:
        BaseAgentChassis(config)
    
    assert "does not implement the expected interface" in str(exc_info.value)
