from fastapi import APIRouter, HTTPException
from smart_wardrobe.schemas.request_schema import RecommendationRequest
from smart_wardrobe.schemas.response_schema import RecommendationResponse
from smart_wardrobe.services.recommendation_service import recommend_outfit

from smart_wardrobe.services.stylist_service import AIStylistEngine

router = APIRouter()

@router.post("/", response_model=RecommendationResponse)
def recommend(request: RecommendationRequest):
    try:
        result = recommend_outfit(request.user_id, request.prompt)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pro")
def recommend_pro(request: RecommendationRequest):
    try:
        result = AIStylistEngine.generate_pro_recommendation(request.user_id, request.prompt, request.city)
        return {"recommendation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))