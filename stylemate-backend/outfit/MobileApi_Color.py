import os
import json
import tempfile
import traceback
import joblib
import numpy as np

from PIL import Image
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse

# -----------------------------------------
# FastAPI Router
# -----------------------------------------
router = APIRouter()

# -----------------------------------------
# Base Paths
# -----------------------------------------
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "color_histogram_classifier.pkl"
)

SCALER_PATH = os.path.join(
    BASE_DIR,
    "models",
    "color_histogram_scaler.pkl"
)

LABEL_ENCODER_PATH = os.path.join(
    BASE_DIR,
    "models",
    "color_histogram_label_encoder.pkl"
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "temp_uploads"
)

# Your actual file location
CONTROL_DATA_PATH = os.path.join(
    BASE_DIR,
    "outfit",
    "data",
    "color_controls.json"
)

# -----------------------------------------
# Allowed Extensions
# -----------------------------------------
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}


def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# -----------------------------------------
# Create Upload Folder
# -----------------------------------------
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -----------------------------------------
# Load Models
# -----------------------------------------
MODEL_ARTIFACTS_AVAILABLE = all(
    os.path.exists(path)
    for path in [
        MODEL_PATH,
        SCALER_PATH,
        LABEL_ENCODER_PATH
    ]
)

if MODEL_ARTIFACTS_AVAILABLE:
    classifier = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    label_encoder = joblib.load(LABEL_ENCODER_PATH)
    print("Color model loaded successfully!")
else:
    classifier = None
    scaler = None
    label_encoder = None
    print("Models not found → fallback mode enabled")


# -----------------------------------------
# Load JSON Control Data
# -----------------------------------------
if not os.path.exists(CONTROL_DATA_PATH):
    raise FileNotFoundError(
        f"{CONTROL_DATA_PATH} not found"
    )

with open(CONTROL_DATA_PATH, "r") as f:
    control_data = json.load(f)


# -----------------------------------------
# Extract Histogram
# -----------------------------------------
def extract_color_histogram(image_path, bins=32):
    try:
        img = Image.open(image_path).convert("RGB")
        img_array = np.array(img)

        hist_r = np.histogram(
            img_array[:, :, 0],
            bins=bins,
            range=(0, 256)
        )[0]

        hist_g = np.histogram(
            img_array[:, :, 1],
            bins=bins,
            range=(0, 256)
        )[0]

        hist_b = np.histogram(
            img_array[:, :, 2],
            bins=bins,
            range=(0, 256)
        )[0]

        features = np.concatenate([
            hist_r,
            hist_g,
            hist_b
        ])

        features = features.astype(float)

        if np.sum(features) > 0:
            features = features / np.sum(features)

        return features

    except Exception as e:
        print("Histogram error:", e)
        return None


# -----------------------------------------
# Fallback Prediction
# -----------------------------------------
def predict_color_fallback(img_path):
    img = Image.open(img_path).convert("RGB").resize((100, 100))
    pixels = np.array(img).reshape(-1, 3)

    avg = pixels.mean(axis=0)

    r, g, b = avg
    max_channel = max(avg)
    min_channel = min(avg)

    if max_channel < 70:
        return "Black", 65.0

    if min_channel > 185:
        return "White", 65.0

    if max_channel - min_channel < 30:
        return "Grey", 60.0

    if r > g and r > b:
        return "Red", 70.0

    if g > r and g > b:
        return "Green", 70.0

    if b > r and b > g:
        return "Blue", 70.0

    return "Brown", 55.0


# -----------------------------------------
# Main Prediction
# -----------------------------------------
def predict_species(img_path):
    try:
        if not MODEL_ARTIFACTS_AVAILABLE:
            return predict_color_fallback(img_path)

        features = extract_color_histogram(img_path)

        if features is None:
            return None, 0.0

        features = features.reshape(1, -1)
        features_scaled = scaler.transform(features)

        prediction_idx = int(
            classifier.predict(features_scaled)[0]
        )

        predicted_class = label_encoder.inverse_transform(
            [prediction_idx]
        )[0]

        probabilities = classifier.predict_proba(
            features_scaled
        )[0]

        confidence = float(
            np.max(probabilities) * 100
        )

        return predicted_class, confidence

    except Exception as e:
        print("Prediction error:", e)
        traceback.print_exc()
        return None, 0.0


# -----------------------------------------
# Health API
# -----------------------------------------
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": MODEL_ARTIFACTS_AVAILABLE,
        "fallback_mode": not MODEL_ARTIFACTS_AVAILABLE
    }


# -----------------------------------------
# Predict API
# -----------------------------------------
@router.post("/predict")
async def predict(
    image: UploadFile = File(...),
    occasion: str = Form("Wedding")
):
    try:
        print("Prediction request received")

        print("Uploaded file:", image.filename)

        if image.filename == "":
            return JSONResponse(
                status_code=400,
                content={"error": "No file selected"}
            )

        if not allowed_file(image.filename):
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Only jpg/jpeg/png files allowed"
                }
            )

        file_ext = (
            os.path.splitext(image.filename)[1].lower()
            or ".jpg"
        )

        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file_ext,
            dir=UPLOAD_FOLDER
        )

        content = await image.read()

        with open(temp_file.name, "wb") as f:
            f.write(content)

        temp_file.close()

        predicted_species, confidence = predict_species(
            temp_file.name
        )

        try:
            os.remove(temp_file.name)
        except:
            pass

        if predicted_species is None:
            return JSONResponse(
                status_code=500,
                content={"error": "Prediction failed"}
            )

        available_occasions = control_data.get(
            "occasions",
            []
        )

        if occasion not in available_occasions:
            occasion = (
                available_occasions[0]
                if available_occasions
                else "Wedding"
            )

        color_info = control_data.get(
            predicted_species,
            {}
        )

        result = {
            "predicted_color": str(predicted_species),
            "confidence": round(float(confidence), 2),
            "description": color_info.get(
                "description",
                ""
            ),
            "dress_pattern_description": color_info.get(
                "dress_pattern_description",
                ""
            ),
            "matching_colors": color_info.get(
                "matching_colors",
                []
            ),
            "occasion": occasion,
            "men_recommendations": color_info.get(
                "recommendations",
                {}
            ).get(
                occasion,
                {}
            ).get(
                "men",
                []
            ),
            "women_recommendations": color_info.get(
                "recommendations",
                {}
            ).get(
                occasion,
                {}
            ).get(
                "women",
                []
            ),
            "status": "success"
        }

        return result

    except Exception as e:
        print("Server error:", e)
        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={
                "error": str(e)
            }
        )