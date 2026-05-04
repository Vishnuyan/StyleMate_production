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

class GroupMatch(BaseModel):
    userA: Dict[str, Any]
    userB: Dict[str, Any]
    score: float

class GroupOutfitItem(BaseModel):
    user: str
    item: Dict[str, Any]

class GroupResponse(BaseModel):
    type: str  # "couple" or "group"
    matches: Optional[List[GroupMatch]] = None  # For couple matching
    theme: Optional[str] = None  # For group matching
    outfits: Optional[List[List[GroupOutfitItem]]] = None  # For group matching