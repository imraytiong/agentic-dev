from typing import Optional
from pydantic import BaseModel, Field

class HelloRequest(BaseModel):
    """
    Incoming payload for the Sparky greeting task.
    """
    developer_name: str = Field(..., description="The name of the developer testing the system.")
    current_mood: str = Field(..., description="How they are feeling about the architecture today.")
    location: Optional[str] = Field(None, description="The user's current city or location for weather updates.")

class HelloState(BaseModel):
    """
    Persistent state for the user's interaction with Sparky.
    """
    interaction_count: int = Field(0, description="Tracks how many times this specific user has pinged Sparky.")
    last_known_location: Optional[str] = Field(None, description="The last location provided by the user.")

class HelloResponse(BaseModel):
    """
    Final structured output returned by Sparky.
    """
    greeting_message: str = Field(..., description="A cute, personalized welcome message.")
    affirmation: str = Field(..., description="A generated affirmation based on their mood.")
    weather_report: Optional[str] = Field(None, description="A weather update based on the user's location, if known.")
    total_interactions: int = Field(..., description="The updated count from the database.")
