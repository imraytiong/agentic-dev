def get_affirmation(mood: str) -> str:
    """
    Returns a nerdy affirmation based on the developer's current mood.
    
    Args:
        mood (str): The current mood of the developer (e.g., 'happy', 'sad', 'stressed').
        
    Returns:
        str: A personalized affirmation.
    """
    mood_lower = mood.lower()
    
    if "happy" in mood_lower or "positive" in mood_lower or "good" in mood_lower:
        return "May your code compile on the first try and your CI/CD pipelines run green! Your Docker containers will be flawless today."
    elif "sad" in mood_lower or "negative" in mood_lower or "frustrated" in mood_lower:
        return "Don't worry, even the best developers face segfaults and cryptic error messages. Take a breath, you've got this."
    elif "stress" in mood_lower or "overwhelmed" in mood_lower or "tired" in mood_lower:
        return "Remember to drink water, stretch, and step away from the keyboard. The bug will be there when you get back, and you'll crush it."
    else:
        return "I'm not sure how to respond to that mood, but I believe in your coding abilities anyway! Keep building awesome things."
