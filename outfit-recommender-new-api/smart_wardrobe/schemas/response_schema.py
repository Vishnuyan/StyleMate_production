from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ClothingItem(BaseModel):
    id: str
    image: str
    type: str
    color: str
    fabric: str

class Outfit(BaseModel):
    id: str
    items: List[ClothingItem]
    score: float
    reason: str

class RecommendationResponse(BaseModel):
    outfits: List[Outfit] = []
    message: Optional[str] = None

class TripDay(BaseModel):
    day: int
    weather: str
    outfit: Outfit

class TripResponse(BaseModel):
    destination: str
    days: int
    daily_plan: List[TripDay]
    packing_list: List[Dict[str, str]]

class GroupCoordination(BaseModel):
    user_id: str
    recommended_outfit: Outfit

class GroupResponse(BaseModel):
    theme: str
    coordinated_outfits: List[GroupCoordination]
    harmony_reason: str