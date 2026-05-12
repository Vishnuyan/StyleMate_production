from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil
import uuid
import json
import re
import base64
from pymongo import MongoClient
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
from openai import OpenAI

from accessories.pipeline.recommender import predict_recommendation

load_dotenv()

router = APIRouter()

# Mongo
MONGO_URL = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URL)

db = client["stylemate"]
collection = db["necklaces"]

# OpenAI
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Upload folder - use absolute path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, "uploaded_accessories")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------------------------------
# Request Model
# ---------------------------------------
class RecommendAccessoryRequest(BaseModel):
    features: dict
    accessories: List[dict]


# ----------------------------------------
# Get Necklace Recommendation
# ----------------------------------------
class FeaturesInput(BaseModel):
    skin_tone: str
    neckline: str
    dress_color: str

@router.post("/recommend")
async def recommend_necklace(
    data: FeaturesInput
):
    """
    Get ML model necklace recommendations
    based on outfit features.
    
    Expected input:
    {
      "skin_tone": "...",
      "neckline": "...",
      "dress_color": "..."
    }
    """
    try:
        skin_tone = data.skin_tone
        neckline = data.neckline
        dress_color = data.dress_color

        print(
            f"[RECOMMEND] "
            f"skin={skin_tone}, "
            f"neck={neckline}, "
            f"color={dress_color}"
        )

        # Get ML recommendation
        model_result = predict_recommendation(
            skin_tone,
            neckline,
            dress_color.lower()
        )

        print(
            f"[MODEL OUTPUT] {model_result}"
        )

        return {
            "model_recommendation": model_result,
            "input": data.dict()
        }

    except Exception as e:
        print(f"[ERROR]: {e}")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ----------------------------------------
@router.post("/upload-accessory")
async def upload_accessory(
    file: UploadFile = File(...)
):
    try:
        if not file:
            return {
                "error": "No file uploaded"
            }

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

        # Convert image to base64 for OpenAI
        with open(filepath, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')

        print(
            f"[UPLOAD] Converted to base64, size: {len(image_data)} bytes"
        )

        # -------- ----------------------------
        # OpenAI classify necklace using base64
        # --------------------------------
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this necklace image and return ONLY valid JSON:
{
  "necklace_type": "pendant/choker/chain/etc",
  "metal": "gold/silver/platinum/etc",
  "color": "color name"
}"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
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
            # Strip markdown code block if present
            clean_result = result.strip()
            if clean_result.startswith("```"):
                clean_result = clean_result.split("```")[1]
                if clean_result.startswith("json"):
                    clean_result = clean_result[4:]
            clean_result = clean_result.strip()
            
            classified_data = json.loads(
                clean_result
            )
        except:
            classified_data = {
                "necklace_type": "pendant",
                "metal": "silver",
                "color": "clear"
            }

        accessory_data = {
            "style":
                classified_data.get(
                    "necklace_type",
                    "necklace"
                ),

            "metal":
                classified_data.get(
                    "metal",
                    "gold"
                ),

            "color":
                classified_data.get(
                    "color",
                    "unknown"
                ),

            "image_url":
                image_url
        }

        db_result = collection.insert_one(
            accessory_data
        )

        return {
            "message":
                "Accessory uploaded successfully",

            "inserted_id":
                str(
                    db_result.inserted_id
                ),

            "metadata": {
                "style": accessory_data.get("style"),
                "metal": accessory_data.get("metal"),
                "color": accessory_data.get("color"),
                "image_url": accessory_data.get("image_url")
            }
        }

    except Exception as e:
        print(e)

        return {
            "error": str(e)
        }


# ---------------------------------------
# Fetch Accessories
# ---------------------------------------
@router.get("/get-accessories")
async def get_accessories():
    try:
        accessories = list(
            collection.find()
        )

        formatted = []

        for item in accessories:
            formatted.append({
                "id":
                    str(item["_id"]),

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
                        "unknown"
                    ),

                "image_url":
                    item.get(
                        "image_url",
                        ""
                    )
            })

        return {
            "accessories":
                formatted
        }

    except Exception as e:
        return {
            "error": str(e)
        }


# ---------------------------------------
# Recommend Best Necklace
# ---------------------------------------
@router.post("/recommend-accessory")
async def recommend_accessory(
    request: RecommendAccessoryRequest
):
    try:
        features = request.features
        accessories = request.accessories

        if not accessories:
            raise HTTPException(
                status_code=400,
                detail="No accessories found"
            )

        skin = features.get(
            "skin_tone"
        )

        neck = features.get(
            "neckline"
        )

        color = features.get(
            "dress_color"
        )

        print(
            f"[USER FEATURES] "
            f"{skin}, {neck}, {color}"
        )

        # -----------------------------
        # Step 1 → ML recommendation
        # -----------------------------
        model_result = predict_recommendation(
            skin,
            neck,
            color.lower()
        )

        recommended_style = (
            model_result.get(
                "necklace_style",
                ""
            )
        )

        recommended_metal = (
            model_result.get(
                "metal",
                ""
            )
        )

        print(
            f"[MODEL OUTPUT] "
            f"Style={recommended_style}, "
            f"Metal={recommended_metal}"
        )

        # -----------------------------
        # Step 2 → Build wardrobe text
        # -----------------------------
        wardrobe_text = ""

        for i, item in enumerate(
            accessories
        ):
            wardrobe_text += f"""
{i+1}.
Style: {item.get('style')}
Metal: {item.get('metal')}
Color: {item.get('color')}
Image: {item.get('image_url')}
"""

        # -----------------------------
        # Step 3 → OpenAI selection
        # -----------------------------
        prompt = f"""
User outfit details:
Skin tone: {skin}
Neckline: {neck}
Dress color: {color}

ML recommendation:
Style: {recommended_style}
Metal: {recommended_metal}

Available necklaces:
{wardrobe_text}

Choose the BEST matching necklace.

Return ONLY this format:

NECKLACE_NUMBER: X

Example:
NECKLACE_NUMBER: 2

Do not return explanations.
Do not return extra text.
"""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
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
            f"[OPENAI RESPONSE]: {result}"
        )

        # -----------------------------
        # Step 4 → Safe parsing
        # -----------------------------
        match = re.search(
            r"NECKLACE_NUMBER:\s*(\d+)",
            result,
            re.IGNORECASE
        )

        if match:
            selected_index = (
                int(
                    match.group(1)
                ) - 1
            )

        else:
            match = re.search(
                r"necklace\s*(\d+)",
                result,
                re.IGNORECASE
            )

            if match:
                selected_index = (
                    int(
                        match.group(1)
                    ) - 1
                )

            else:
                print(
                    "[FALLBACK] Rule-based selection"
                )

                best_score = -1
                best_index = 0

                for i, item in enumerate(
                    accessories
                ):
                    score = 0

                    if item.get(
                        "style"
                    ) == recommended_style:
                        score += 2

                    if item.get(
                        "metal"
                    ) == recommended_metal:
                        score += 2

                    if item.get(
                        "color"
                    ) == color:
                        score += 1

                    if score > best_score:
                        best_score = score
                        best_index = i

                selected_index = best_index

        if (
            selected_index < 0
            or selected_index >= len(accessories)
        ):
            raise HTTPException(
                status_code=500,
                detail="Invalid selection index"
            )

        best_match = accessories[
            selected_index
        ]

        # Convert ObjectId to string
        if best_match and "_id" in best_match:
            best_match["_id"] = str(best_match["_id"])

        return {
            "model_recommendation":
                model_result,

            "best_match":
                best_match
        }

    except Exception as e:
        print(
            f"[ERROR]: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )