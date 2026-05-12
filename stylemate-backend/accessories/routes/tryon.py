import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from services.openai_tryon import generate_tryon
from utils.file_save import save_output_image

router = APIRouter()

BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)

TEMP_DIR = os.path.join(
    BASE_DIR,
    "accessories",
    "temp_uploads"
)

os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/virtual-tryon")
async def virtual_tryon(
    person_image: UploadFile = File(...),
    necklace_image: UploadFile = File(...)
):
    try:
        # Save uploaded files temporarily
        person_ext = os.path.splitext(person_image.filename)[1] or ".png"
        necklace_ext = os.path.splitext(necklace_image.filename)[1] or ".png"

        person_temp_path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}_person{person_ext}")
        necklace_temp_path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}_necklace{necklace_ext}")

        with open(person_temp_path, "wb") as f:
            f.write(await person_image.read())

        with open(necklace_temp_path, "wb") as f:
            f.write(await necklace_image.read())

        # Send to OpenAI
        output_bytes = generate_tryon(person_temp_path, necklace_temp_path)

        # Save final result
        saved_path, filename = save_output_image(output_bytes, ".png")

        # Clean temp files
        if os.path.exists(person_temp_path):
            os.remove(person_temp_path)
        if os.path.exists(necklace_temp_path):
            os.remove(necklace_temp_path)

        return JSONResponse({
            "success": True,
            "image_url": f"/generated/{filename}",
            "filename": filename
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))