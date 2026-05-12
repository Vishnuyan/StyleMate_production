# from fastapi import APIRouter
# from services.wardrobe_recommend import recommend_best_necklace

# router = APIRouter()

# @router.post("/wardrobe/recommend")
# def recommend(data: dict):
#     features = data["features"]
#     necklaces = data["necklaces"]

#     result = recommend_best_necklace(
#         features,
#         necklaces
#     )

#     return {
#         "recommended_id": result
#     }