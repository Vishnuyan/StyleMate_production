from fastapi import APIRouter
from accessories.database.mongo import necklace_collection

router = APIRouter()


# ---------------------------------------
# Get user's saved wardrobe necklaces
# ---------------------------------------
@router.get("/{user_id}")
def get_user_wardrobe(user_id: str):
    try:
        items = list(
            necklace_collection.find(
                {"user_id": user_id},
                {"_id": 0}
            )
        )

        return {
            "necklaces": items
        }

    except Exception as e:
        return {
            "error": str(e)
        }


# ---------------------------------------
# Recommend best necklace
# ---------------------------------------
@router.post("/recommend")
def recommend_from_wardrobe(data: dict):
    try:
        features = data.get(
            "features",
            {}
        )

        necklaces = data.get(
            "necklaces",
            []
        )

        if not necklaces:
            return {
                "error":
                "No necklaces found"
            }

        skin_tone = features.get(
            "skin_tone"
        )

        neckline = features.get(
            "neckline"
        )

        dress_color = features.get(
            "dress_color"
        )

        print(
            f"[USER FEATURES] "
            f"skin={skin_tone}, "
            f"neckline={neckline}, "
            f"color={dress_color}"
        )

        best_match = None
        best_score = -1

        for item in necklaces:
            score = 0

            print(
                f"[CHECKING] "
                f"{item.get('id')}"
            )

            # neckline match
            if (
                item.get(
                    "suitable_neckline"
                ) == neckline
            ):
                score += 3

            # skin tone match
            if (
                item.get(
                    "suitable_skin_tone"
                ) == skin_tone
            ):
                score += 3

            # dress color match
            if (
                item.get(
                    "suitable_dress_color"
                ) == dress_color
            ):
                score += 3

            # style bonus
            if item.get("style"):
                score += 1

            print(
                f"[SCORE] "
                f"{item.get('id')} "
                f"= {score}"
            )

            # use >= to avoid always selecting first item
            if score >= best_score:
                best_score = score
                best_match = item

        if not best_match:
            return {
                "error":
                "No suitable necklace found"
            }

        print(
            f"[BEST MATCH] "
            f"{best_match.get('id')}"
        )

        return {
            "recommended_id":
                best_match.get("id"),

            "recommended_necklace":
                best_match,

            "score":
                best_score
        }

    except Exception as e:
        print(
            f"[ERROR] {e}"
        )

        return {
            "error": str(e)
        }