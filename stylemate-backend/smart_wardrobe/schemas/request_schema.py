from pydantic import BaseModel, Field
from typing import List

class RecommendationRequest(BaseModel):
    user_id: str = Field(..., example="user_123")
    prompt: str = Field(..., example="casual outfit for a summer party")
    city: str = Field(None, example="New York")


class TripRequest(BaseModel):
    user_id: str = Field(..., example="user_123")
    city: str = Field(..., example="Paris")
    days: int = Field(..., gt=0, example=3)

class GroupRequest(BaseModel):
    user_ids: List[str] = Field(..., example=["user_1", "user_2"])
    prompt: str = Field(..., example="matching outfits for a date night")