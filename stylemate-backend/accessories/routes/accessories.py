from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil
import uuid
import json
import base64
from pymongo import MongoClient
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
from bson import ObjectId
from openai import OpenAI

load_dotenv()

router = APIRouter()

# Mongo connection
MONGO_URL = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URL)

db = client["stylemate"]
collection = db["necklaces"]

# OpenAI
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Local folder
UPLOAD_FOLDER = "uploaded_accessories"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -----------------------------------
# Request model
# -----------------------------------
class RecommendAccessoryRequest(BaseModel):
    features: dict
    accessories: List[dict]


# -----------------------------------
# Upload accessory
# -----------------------------------
@router.post("/upload-accessory")
async def upload_accessory(
    file: UploadFile = File(...)
):
    try:
        if not file:
            return {
                "error": "No file uploaded"
            }

        # -------------------------
        # Save image locally
        # -------------------------
        file_ext = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{file_ext}"

        filepath = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        image_url = (
            f"http://localhost:8000/"
            f"{UPLOAD_FOLDER}/{filename}"
        )

        print(
            f"[UPLOAD] Saved: {image_url}"
        )

        # -------------------------
        # Convert image → base64
        # -------------------------
        with open(filepath, "rb") as image_file:
            image_data = base64.b64encode(
                image_file.read()
            ).decode("utf-8")

        print(
            f"[UPLOAD] Converted to base64"
        )

        # -------------------------
        # OpenAI analyze necklace
        # -------------------------
        analysis_prompt = """
Analyze this necklace image carefully.

Identify:

1. necklace_style
(ex: chain, pendant, lariat, choker, statement)

2. metal
(ex: gold, silver, rose gold, platinum, mixed)

3. color
(dominant necklace color)

4. suitable_neckline
(ex: vneck, round, square, strapless, offshoulder, highneck)

5. suitable_skin_tone
(ex: light, mid-light, mid-dark, dark)

6. suitable_dress_color
(ex: red, blue, black, teal, purple)

Return JSON only:

{
 "necklace_style":"",
 "metal":"",
 "color":"",
 "suitable_neckline":"",
 "suitable_skin_tone":"",
 "suitable_dress_color":""
}
"""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": analysis_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url":
                                f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ]
        )

        result = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        print(
            f"[CLASSIFICATION]: {result}"
        )

        try:
            clean_result = result.strip()

            if clean_result.startswith("```"):
                clean_result = (
                    clean_result
                    .replace("```json", "")
                    .replace("```", "")
                    .strip()
                )

            classified_data = json.loads(
                clean_result
            )

        except Exception:
            print(
                "[FALLBACK] Using defaults"
            )

            classified_data = {
                "necklace_style": "chain",
                "metal": "gold",
                "color": "gold",
                "suitable_neckline": "all",
                "suitable_skin_tone": "all",
                "suitable_dress_color": "all"
            }

        # -------------------------
        # Save metadata
        # -------------------------
        accessory_data = {
            "id":
                str(uuid.uuid4()),

            "user_id":
                "default_user",

            "style":
                classified_data.get(
                    "necklace_style",
                    "chain"
                ),

            "metal":
                classified_data.get(
                    "metal",
                    "gold"
                ),

            "color":
                classified_data.get(
                    "color",
                    "gold"
                ),

            "suitable_neckline":
                classified_data.get(
                    "suitable_neckline",
                    "all"
                ),

            "suitable_skin_tone":
                classified_data.get(
                    "suitable_skin_tone",
                    "all"
                ),

            "suitable_dress_color":
                classified_data.get(
                    "suitable_dress_color",
                    "all"
                ),

            "image_url":
                image_url
        }

        db_result = collection.insert_one(
            accessory_data
        )

        print(
            f"[SAVED]: {accessory_data}"
        )

        # -------------------------
        # Safe response
        # -------------------------
        safe_metadata = {
            "id":
                accessory_data.get("id"),

            "user_id":
                accessory_data.get("user_id"),

            "style":
                accessory_data.get("style"),

            "metal":
                accessory_data.get("metal"),

            "color":
                accessory_data.get("color"),

            "suitable_neckline":
                accessory_data.get(
                    "suitable_neckline"
                ),

            "suitable_skin_tone":
                accessory_data.get(
                    "suitable_skin_tone"
                ),

            "suitable_dress_color":
                accessory_data.get(
                    "suitable_dress_color"
                ),

            "image_url":
                accessory_data.get(
                    "image_url"
                )
        }

        return {
            "message":
                "Accessory uploaded successfully",

            "inserted_id":
                str(
                    db_result.inserted_id
                ),

            "image_url":
                image_url,

            "metadata":
                safe_metadata
        }

    except Exception as e:
        print(
            f"[ERROR]: {e}"
        )

        return {
            "error": str(e)
        }

# -----------------------------------
# Fetch accessories
# -----------------------------------
@router.get("/get-accessories")
async def get_accessories():
    try:
        accessories = list(
            collection.find()
        )

        formatted_accessories = []

        for item in accessories:
            formatted_accessories.append({
                "id":
                    str(item["_id"]),

                "custom_id":
                    item.get(
                        "id",
                        ""
                    ),

                "user_id":
                    item.get(
                        "user_id",
                        ""
                    ),

                "style":
                    item.get(
                        "style",
                        "necklace"
                    ),

                "metal":
                    item.get(
                        "metal",
                        "gold"
                    ),

                "color":
                    item.get(
                        "color",
                        "gold"
                    ),

                # FIX → retrieve saved compatibility fields
                "suitable_neckline":
                    item.get(
                        "suitable_neckline",
                        "all"
                    ),

                "suitable_skin_tone":
                    item.get(
                        "suitable_skin_tone",
                        "all"
                    ),

                "suitable_dress_color":
                    item.get(
                        "suitable_dress_color",
                        "all"
                    ),

                "image_url":
                    item.get(
                        "image_url",
                        ""
                    )
            })

        print(
            f"[FETCHED ACCESSORIES]: "
            f"{formatted_accessories}"
        )

        return {
            "accessories":
                formatted_accessories
        }

    except Exception as e:
        print(
            f"[FETCH ERROR]: {e}"
        )

        return {
            "error": str(e)
        }

# -----------------------------------
# Recommend best accessory
# -----------------------------------
@router.post("/recommend-accessory")
async def recommend_accessory(
    request: RecommendAccessoryRequest
):
    try:
        features = request.features
        accessories = request.accessories

        if not accessories:
            return {
                "error":
                "No accessories found"
            }

        skin_tone = features.get(
            "skin_tone",
            ""
        ).lower().strip()

        neckline = features.get(
            "neckline",
            ""
        ).lower().strip()

        dress_color = features.get(
            "dress_color",
            ""
        ).lower().strip()

        print(
            f"\n[WARDROBE RECOMMENDATION]"
        )
        print(
            f"User Features:"
        )
        print(
            f"  skin_tone: {skin_tone}"
        )
        print(
            f"  neckline: {neckline}"
        )
        print(
            f"  dress_color: {dress_color}"
        )
        print(
            f"\n[SCORING {len(accessories)} ACCESSORIES]"
        )

        best_match = None
        best_score = -1
        scores_list = []

        for i, item in enumerate(accessories):
            score = 0
            reasons = []

            necklace_style = item.get(
                "style",
                ""
            ).lower().strip()
            
            necklace_metal = item.get(
                "metal",
                ""
            ).lower().strip()
            
            necklace_color = item.get(
                "color",
                ""
            ).lower().strip()

            print(
                f"\n  Necklace #{i+1}:"
            )
            print(
                f"    style: {necklace_style}"
            )
            print(
                f"    metal: {necklace_metal}"
            )
            print(
                f"    color: {necklace_color}"
            )

            # ─────────────────────────
            # Metal-Color Harmony
            # ─────────────────────────
            warm_dress_colors = [
                "gold",
                "orange",
                "brown",
                "red",
                "maroon",
                "copper",
                "warm",
                "yellow"
            ]
            
            cool_dress_colors = [
                "silver",
                "blue",
                "purple",
                "gray",
                "cool",
                "teal",
                "emerald"
            ]

            warm_metals = [
                "gold",
                "rose gold",
                "copper",
                "bronze"
            ]
            
            cool_metals = [
                "silver",
                "platinum",
                "white gold"
            ]

            # Warm metal with warm dress
            if (any(
                warm_color in dress_color
                for warm_color in warm_dress_colors
            ) and any(
                warm_metal in necklace_metal
                for warm_metal in warm_metals
            )):
                score += 5
                reasons.append(
                    "warm metal + warm dress"
                )

            # Cool metal with cool dress
            elif (any(
                cool_color in dress_color
                for cool_color in cool_dress_colors
            ) and any(
                cool_metal in necklace_metal
                for cool_metal in cool_metals
            )):
                score += 5
                reasons.append(
                    "cool metal + cool dress"
                )

            # ─────────────────────────
            # Direct Metal Match
            # ─────────────────────────
            if dress_color in necklace_metal:
                score += 3
                reasons.append(
                    "metal matches color"
                )

            # ─────────────────────────
            # Style Versatility
            # ─────────────────────────
            versatile_styles = [
                "chain",
                "pendant",
                "locket"
            ]
            
            if any(
                style in necklace_style
                for style in versatile_styles
            ):
                score += 2
                reasons.append(
                    f"versatile {necklace_style}"
                )

            # ─────────────────────────
            # Necklace Color Match
            # ─────────────────────────
            if necklace_color == dress_color:
                score += 2
                reasons.append(
                    "color matches"
                )

            # Black/white necklaces
            # work with everything
            if necklace_color in [
                "black",
                "white",
                "clear"
            ]:
                score += 1
                reasons.append(
                    f"{necklace_color} universal"
                )

            # ─────────────────────────
            # Skin Tone Match
            # ─────────────────────────
            if skin_tone in [
                "dark",
                "mid-dark"
            ]:
                if any(
                    warm in necklace_metal
                    for warm in warm_metals
                ):
                    score += 2
                    reasons.append(
                        "gold for dark skin"
                    )

            elif skin_tone in [
                "light",
                "mid-light"
            ]:
                if any(
                    cool in necklace_metal
                    for cool in cool_metals
                ):
                    score += 2
                    reasons.append(
                        "silver for light skin"
                    )

            # ─────────────────────────
            # Final Score
            # ─────────────────────────
            reason_text = (
                " + ".join(reasons)
                if reasons
                else "no matches"
            )

            print(
                f"    Score: {score}"
            )
            print(
                f"    Reasons: {reason_text}"
            )

            scores_list.append({
                "index": i,
                "score": score,
                "item": item
            })

            # Strict > comparison
            if score > best_score:
                best_score = score
                best_match = item
                best_index = i
                print(
                    f"    ✓ NEW BEST"
                )

        print(f"\n[SUMMARY]")
        print(
            f"Scores: "
            f"{[s['score'] for s in scores_list]}"
        )

        # Handle tie - pick random
        # among best options
        if best_match:
            tied_items = [
                s for s in scores_list
                if s['score'] == best_score
            ]

            if len(tied_items) > 1:
                import random
                best_match = random.choice(
                    tied_items
                )['item']
                print(
                    f"Tie detected! "
                    f"Randomly selected from "
                    f"{len(tied_items)} options"
                )

        if not best_match:
            # True fallback - pick
            # random, not first
            import random
            best_match = random.choice(
                accessories
            )
            best_score = 0
            print(
                "[FALLBACK] "
                "Random selection"
            )

        print(
            f"\n[FINAL] "
            f"Best match score: {best_score}\n"
        )

        # Convert ObjectId to string
        if best_match and "_id" in best_match:
            best_match["_id"] = str(best_match["_id"])

        return {
            "message":
                "Best necklace selected",
            "best_match":
                best_match,
            "score":
                best_score
        }

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "error": str(e)
        }


# -----------------------------------
# Delete accessory
# -----------------------------------
@router.delete("/delete-accessory/{accessory_id}")
async def delete_accessory(
    accessory_id: str
):
    try:
        item = collection.find_one({
            "_id": ObjectId(
                accessory_id
            )
        })

        if not item:
            return {
                "error":
                "Accessory not found"
            }

        image_url = item.get(
            "image_url",
            ""
        )

        if image_url:
            filename = image_url.split("/")[-1]

            filepath = os.path.join(
                UPLOAD_FOLDER,
                filename
            )

            if os.path.exists(filepath):
                os.remove(filepath)

        collection.delete_one({
            "_id": ObjectId(
                accessory_id
            )
        })

        return {
            "message":
                "Accessory deleted successfully"
        }

    except Exception as e:
        return {
            "error": str(e)
        }