from fastapi import APIRouter, UploadFile, File, HTTPException
from io import BytesIO
from PIL import Image
import sys
import os
import tempfile

# Add backend root to path
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from pipeline.skin_tone import predict_skin_tone
from pipeline.neckline import predict_neckline
from pipeline.dress_color import detect_dress_color

# NEW
from services.openai_fallback import extract_with_openai

router = APIRouter()


@router.post("/extract")
async def extract_features(
    file: UploadFile = File(...)
):
    try:
        if file.content_type not in [
            "image/jpeg",
            "image/png",
            "image/webp"
        ]:
            raise HTTPException(
                status_code=400,
                detail="Only JPG, PNG, WebP images are accepted"
            )

        contents = await file.read()

        if len(contents) == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )

        print(
            f"[EXTRACT] Processing: "
            f"{file.filename} "
            f"({len(contents)} bytes)"
        )

        base_img = Image.open(
            BytesIO(contents)
        ).convert("RGB")

        print(
            f"[EXTRACT] Image loaded, size: {base_img.size}"
        )

        skin_img = base_img.copy()
        neck_img = base_img.copy()
        color_img = base_img.copy()

        print(
            "[EXTRACT] Starting model extraction..."
        )

        # -----------------------------
        # MODEL PREDICTIONS
        # -----------------------------
        model_skin = predict_skin_tone(
            skin_img
        )

        model_neck = predict_neckline(
            neck_img
        )

        model_color = detect_dress_color(
            color_img
        )

        print(
            f"[MODEL RESULTS] "
            f"skin={model_skin}, "
            f"neck={model_neck}, "
            f"color={model_color}"
        )

        # -----------------------------
        # SAVE TEMP IMAGE FOR OPENAI
        # -----------------------------
        temp_path = None

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".jpg"
        ) as temp_file:
            temp_file.write(contents)
            temp_path = temp_file.name

        # -----------------------------
        # OPENAI PREDICTIONS
        # -----------------------------
        print(
            "[OPENAI] Starting OpenAI extraction..."
        )

        ai_result = extract_with_openai(
            temp_path
        )

        print(
            f"[OPENAI RESULTS] {ai_result}"
        )

        # delete temp file
        if temp_path and os.path.exists(
            temp_path
        ):
            os.remove(temp_path)

        # -----------------------------
        # COMPARE MODEL VS OPENAI
        # Same → model output
        # Different → OpenAI output
        # -----------------------------

        final_skin = model_skin
        final_neck = model_neck
        final_color = model_color

        if ai_result:
            if (
                ai_result.get(
                    "skin_tone"
                )
                != model_skin
            ):
                final_skin = ai_result.get(
                    "skin_tone"
                ) or model_skin

            if (
                ai_result.get(
                    "neckline"
                )
                != model_neck
            ):
                final_neck = ai_result.get(
                    "neckline"
                ) or model_neck

            if (
                ai_result.get(
                    "dress_color"
                )
                != str(model_color).lower()
            ):
                final_color = ai_result.get(
                    "dress_color"
                ) or model_color

        print(
            f"[FINAL RESULTS] "
            f"skin={final_skin}, "
            f"neck={final_neck}, "
            f"color={final_color}"
        )

        return {
            "skin_tone": final_skin,
            "neckline": final_neck,
            "dress_color": final_color,
        }

    except HTTPException:
        raise

    except Exception as e:
        print(
            f"[ERROR] in extract_features: "
            f"{type(e).__name__}: {e}"
        )

        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Feature extraction failed: {type(e).__name__}: {str(e)}"
        )