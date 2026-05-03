from fastapi import APIRouter, HTTPException
from smart_wardrobe.schemas.request_schema import TripRequest
from smart_wardrobe.schemas.response_schema import TripResponse
from smart_wardrobe.services.trip_service import plan_trip

router = APIRouter()

@router.post("/", response_model=TripResponse)
def trip(request: TripRequest):
    try:
        result = plan_trip(request.user_id, request.city, request.days)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))