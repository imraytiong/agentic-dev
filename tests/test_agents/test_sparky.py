import pytest
from src.agents.hello_sparky.tools import get_affirmation

def test_get_affirmation_positive():
    affirmation = get_affirmation("happy")
    assert "compile" in affirmation.lower() or "green" in affirmation.lower() or "docker" in affirmation.lower()

def test_get_affirmation_negative():
    affirmation = get_affirmation("sad")
    assert "breath" in affirmation.lower() or "got this" in affirmation.lower() or "segfaults" in affirmation.lower()

def test_get_affirmation_stressed():
    affirmation = get_affirmation("stressed")
    assert "water" in affirmation.lower() or "stretch" in affirmation.lower() or "step away" in affirmation.lower()

def test_get_affirmation_unknown():
    affirmation = get_affirmation("hungry")
    assert "believe" in affirmation.lower() or "abilities" in affirmation.lower()

# Note: Agent integration tests will be added after the agent logic is implemented 
# using `chassis.run_local(mock_infrastructure=True)`.