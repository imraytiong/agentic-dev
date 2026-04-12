import pytest
from src.agents.hello_sparky.tools import get_affirmation, get_weather

def test_get_affirmation_logic():
    assert "CI/CD" in get_affirmation("happy")
    assert "CI/CD" in get_affirmation("excited")
    assert "segfaults" in get_affirmation("sad")
    assert "water" in get_affirmation("stress")
    assert "coding abilities" in get_affirmation("unknown")

def test_get_weather_known_location():
    # Test for a city that will be in our 20-location dictionary
    report = get_weather("New York")
    assert "New York" in report
    assert "available" not in report.lower()

def test_get_weather_unknown_location():
    # Test for a city that is definitely not in the dictionary
    report = get_weather("Atlantis")
    assert "Weather data not available for Atlantis" in report
