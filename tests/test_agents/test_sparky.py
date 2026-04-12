import pytest
from src.agents.hello_sparky.tools import get_affirmation, get_weather

def test_get_affirmation_logic():
    assert "CI/CD" in get_affirmation("happy")
    assert "CI/CD" in get_affirmation("excited")
    assert "segfaults" in get_affirmation("sad")
    assert "water" in get_affirmation("stress")
    assert "coding abilities" in get_affirmation("unknown")

def test_get_weather_logic():
    # New weather tool tests
    assert "New York" in get_weather("New York")
    assert "not available" in get_weather("UnknownCity").lower()

# Note: Full agent integration tests using chassis.run_local() 
# will be executed in the Validation phase after Layer 4.
