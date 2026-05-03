from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from bson import ObjectId

from smart_wardrobe.services.upload_service import process_upload
from smart_wardrobe.core.database import wardrobe_collection

router = APIRouter()


# Upload wardrobe item
@router.post("/upload")
def upload(
    file: UploadFile = File(...),
    user_id: str = Query(...),
    enhance_with_ai: bool = Query(True)
):
    return process_upload(file, user_id, enhance_with_ai)


# Get all wardrobe items for user
@router.get("/")
def get_wardrobe(user_id: str = Query(...)):
    items = list(
        wardrobe_collection.find({"userId": user_id})
    )

    for item in items:
        item["_id"] = str(item["_id"])

    return {"items": items}


# Delete wardrobe item
@router.delete("/{item_id}")
def delete_wardrobe_item(item_id: str):
    try:
        result = wardrobe_collection.delete_one(
            {"_id": ObjectId(item_id)}
        )

        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Wardrobe item not found"
            )

        return {
            "message": "Wardrobe item deleted successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Delete failed: {str(e)}"
        )