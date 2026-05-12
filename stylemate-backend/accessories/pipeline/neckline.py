import os
import sys
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import pandas as pd
from efficientnet_pytorch import EfficientNet

# ----------------------------------------------------
# Paths
# ----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "../models/neckline/best_neckline_b0.pth")
#CSV_PATH = r"C:\Users\User\Documents\Accessories Suggestion\Neckline\dataset\train\_classes.csv"

print(f"[NECKLINE] Module loading...", file=sys.stderr, flush=True)
print(f"[NECKLINE] MODEL_PATH: {MODEL_PATH}", file=sys.stderr, flush=True)
# print(f"[NECKLINE] CSV_PATH: {CSV_PATH}", file=sys.stderr, flush=True)
print(f"[NECKLINE] Model exists: {os.path.exists(MODEL_PATH)}", file=sys.stderr, flush=True)
# print(f"[NECKLINE] CSV exists: {os.path.exists(CSV_PATH)}", file=sys.stderr, flush=True)
print(f"[NECKLINE] Torch: {torch.__version__}", file=sys.stderr, flush=True)

# ----------------------------------------------------
# Device
# ----------------------------------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[NECKLINE] Using device: {device}", file=sys.stderr, flush=True)

# ----------------------------------------------------
# Load class names from CSV
# ----------------------------------------------------
# if not os.path.exists(CSV_PATH):
#     raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")

# df = pd.read_csv(CSV_PATH)

# CLASSES = [
#     col for col in df.columns
#     if col.lower() not in ["label", "filename"]
# ]

# if len(CLASSES) == 0:
#     raise ValueError("No class names found in CSV.")

# print(f"[NECKLINE] Classes: {CLASSES}", file=sys.stderr, flush=True)

# ----------------------------------------------------
# Globals
# ----------------------------------------------------
_model = None
_model_load_error = None

# ----------------------------------------------------
# Transform
# ----------------------------------------------------
_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# ----------------------------------------------------
# Load model
# ----------------------------------------------------
def _load_model():
    global _model, _model_load_error

    if _model is not None:
        print("[NECKLINE] Using cached model", file=sys.stderr, flush=True)
        return _model

    if _model_load_error is not None:
        print(f"[NECKLINE] Previous load failed: {_model_load_error}", file=sys.stderr, flush=True)
        return None

    try:
        print("[NECKLINE] Creating EfficientNet-B0...", file=sys.stderr, flush=True)

        model = EfficientNet.from_pretrained("efficientnet-b0")
        model._fc = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(model._fc.in_features, len(CLASSES))
        )

        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

        print("[NECKLINE] Loading weights...", file=sys.stderr, flush=True)
        state_dict = torch.load(MODEL_PATH, map_location=device)

        # IMPORTANT: strict=True
        model.load_state_dict(state_dict, strict=True)

        model = model.to(device)
        model.eval()

        _model = model
        print("[NECKLINE] ✓ Model READY", file=sys.stderr, flush=True)
        return _model

    except Exception as e:
        _model_load_error = str(e)
        print(f"[NECKLINE] FATAL: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return None


# Eager load
print("[NECKLINE] Attempting eager load at import...", file=sys.stderr, flush=True)
_load_model()

# ----------------------------------------------------
# Prediction
# ----------------------------------------------------
def predict_neckline(img: Image.Image) -> str:
    try:
        if _model is None:
            print(f"[NECKLINE] ERROR: Model not loaded. Error was: {_model_load_error}", file=sys.stderr, flush=True)
            return "Unknown"

        if not isinstance(img, Image.Image):
            raise TypeError("Input must be a PIL Image")

        img = img.convert("RGB")

        # IMPORTANT:
        # Use full image first because your working code uses full image.
        tensor = _transform(img).unsqueeze(0).to(device)

        with torch.no_grad():
            outputs = _model(tensor)
            probs = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probs, 1)

        result = CLASSES[predicted.item()]
        print(f"[NECKLINE] ✓ Prediction: {result} | Confidence: {confidence.item():.4f}", file=sys.stderr, flush=True)
        return result

    except Exception as e:
        print(f"[NECKLINE] Prediction error: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return "Unknown"