from fastapi import APIRouter, HTTPException
from smart_wardrobe.schemas.request_schema import GroupRequest
from smart_wardrobe.schemas.response_schema import GroupResponse
from smart_wardrobe.services.group_service import group_outfit_multi_user

router = APIRouter()

@router.post("/multi", response_model=GroupResponse)
def group_multi(request: GroupRequest):
    try:
        result = group_outfit_multi_user(request.user_ids, request.prompt)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))