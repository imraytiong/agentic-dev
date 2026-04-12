def get_affirmation(mood: str) -> str:
    """
    Returns a nerdy affirmation based on the developer's current mood.
    
    Args:
        mood (str): The current mood of the developer (e.g., 'happy', 'sad', 'stressed').
        
    Returns:
        str: A personalized affirmation.
    """
    mood_lower = mood.lower()
    
    if "happy" in mood_lower or "positive" in mood_lower or "good" in mood_lower or "excited" in mood_lower or "pumped" in mood_lower:
        return "May your code compile on the first try and your CI/CD pipelines run green! Your Docker containers will be flawless today."
    elif "sad" in mood_lower or "negative" in mood_lower or "frustrated" in mood_lower:
        return "Don't worry, even the best developers face segfaults and cryptic error messages. Take a breath, you've got this."
    elif "stress" in mood_lower or "overwhelmed" in mood_lower or "tired" in mood_lower:
        return "Remember to drink water, stretch, and step away from the keyboard. The bug will be there when you get back, and you'll crush it."
    else:
        return "I'm not sure how to respond to that mood, but I believe in your coding abilities anyway! Keep building awesome things."

def get_weather(location: str) -> str:
    """
    A mock tool that returns the current weather for a given city.
    
    Args:
        location (str): The name of the city to check.
        
    Returns:
        str: A weather report or a 'not available' message.
    """
    # Mock weather database with 20 locations
    WEATHER_DATABASE = {
        "New York": "Sunny, 75°F",
        "London": "Rainy, 55°F",
        "Tokyo": "Cloudy, 68°F",
        "Paris": "Partly Cloudy, 62°F",
        "Sydney": "Clear, 82°F",
        "Berlin": "Windy, 50°F",
        "Dubai": "Hot and Clear, 105°F",
        "Moscow": "Snowing, 28°F",
        "Mumbai": "Humid, 88°F",
        "Rio de Janeiro": "Tropical, 79°F",
        "Cairo": "Dry, 95°F",
        "Toronto": "Chilly, 45°F",
        "Rome": "Sunny, 72°F",
        "Singapore": "Thundershowers, 84°F",
        "Mexico City": "Mild, 70°F",
        "Seoul": "Breezy, 65°F",
        "Cape Town": "Coastal Winds, 66°F",
        "San Francisco": "Foggy, 58°F",
        "Bangkok": "Hazy, 90°F",
        "Amsterdam": "Overcast, 52°F"
    }
    
    # Normalize input for better matching
    location_key = location.strip().title()
    
    if location_key in WEATHER_DATABASE:
        return f"Current weather in {location_key}: {WEATHER_DATABASE[location_key]}."
    else:
        return f"Weather data not available for {location}."
