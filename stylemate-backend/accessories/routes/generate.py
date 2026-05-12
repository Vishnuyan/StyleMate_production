from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
import os
import uuid
import shutil
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai_layer.prompt_writer import build_sdxl_prompt
from generation.comfyui_client import generate_necklace_image
from generation.image_cache import cache_image

router = APIRouter()

class InputData(BaseModel):
    skin_tone: str
    neckline: str = None  # optional, not needed for prompt generation
    dress_color: str

class RecommendationInput(BaseModel):
    necklace_style: str
    metal: str
    input: InputData  # nested input field from recommendation response

class PromptInput(BaseModel):
    prompt: str

@router.post("/generate/prompt")
def get_sdxl_prompt(data: RecommendationInput):
    try:
        # Extract skin_tone and dress_color from nested input field
        prompt_data = {
            "necklace_style": data.necklace_style,
            "metal": data.metal,
            "skin_tone": data.input.skin_tone,
            "dress_color": data.input.dress_color,
        }
        prompt = build_sdxl_prompt(prompt_data)
        return {"prompt": prompt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/image")
def generate_image(data: PromptInput):
    try:
        # Generate the image
        image_url = generate_necklace_image(data.prompt)

        # Save image into local backend folder so frontend can use it safely
        os.makedirs("generated", exist_ok=True)
        filename = f"{uuid.uuid4()}.png"
        saved_path = os.path.join("generated", filename)

        if image_url.startswith("http://") or image_url.startswith("https://"):
            response = requests.get(image_url, stream=True, timeout=60)
            response.raise_for_status()
            with open(saved_path, "wb") as f:
                for chunk in response.iter_content(8192):
                    if chunk:
                        f.write(chunk)
        else:
            local_source = image_url
            if image_url.startswith("/"):
                local_source = image_url[1:]

            if not os.path.isabs(local_source):
                local_source = os.path.join(os.getcwd(), local_source)

            if not os.path.exists(local_source):
                raise FileNotFoundError(f"Generated image not found: {local_source}")

            shutil.copyfile(local_source, saved_path)

        local_image_url = f"/generated/{filename}"
        
        # Cache the result
        cache_image(data.prompt, local_image_url)
        
        return {"image_url": local_image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))