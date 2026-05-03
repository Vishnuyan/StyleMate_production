import torch
import torchvision
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import os
import sys

CLASSES = ["dark", "light", "mid-dark", "mid-light"]
MODEL_PATH = os.path.join(os.path.dirname(__file__), "../models/skin_tone/skin_tone_effnet_b0.pth")

print(f"[SKIN_TONE] Module loading... Model at: {MODEL_PATH}", file=sys.stderr, flush=True)
print(f"[SKIN_TONE] Model exists: {os.path.exists(MODEL_PATH)}", file=sys.stderr, flush=True)
print(f"[SKIN_TONE] Torch: {torch.__version__}, Torchvision: {torchvision.__version__}", file=sys.stderr, flush=True)

_model = None
_model_load_error = None

def _load_model():
    global _model, _model_load_error
    if _model is not None:
        print("[SKIN_TONE] Using cached model", file=sys.stderr, flush=True)
        return _model
    if _model_load_error is not None:
        print(f"[SKIN_TONE] Previous load failed: {_model_load_error}", file=sys.stderr, flush=True)
        return None
    
    print("[SKIN_TONE] Loading model now...", file=sys.stderr, flush=True)
    try:
        print("[SKIN_TONE] Creating EfficientNet B0...", file=sys.stderr, flush=True)
        try:
            m = models.efficientnet_b0(weights=None)
        except TypeError:
            print("[SKIN_TONE] weights=None failed, trying pretrained=False", file=sys.stderr, flush=True)
            m = models.efficientnet_b0(pretrained=False)
        except Exception as e:
            print(f"[SKIN_TONE] Model creation error: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
            raise
        
        print("[SKIN_TONE] Replacing classifier...", file=sys.stderr, flush=True)
        m.classifier[1] = torch.nn.Linear(1280, len(CLASSES))
        
        if os.path.exists(MODEL_PATH):
            print(f"[SKIN_TONE] Loading weights from {MODEL_PATH}...", file=sys.stderr, flush=True)
            state = torch.load(MODEL_PATH, map_location="cpu")
            m.load_state_dict(state, strict=False)
            print("[SKIN_TONE] ✓ Weights loaded", file=sys.stderr, flush=True)
        else:
            print(f"[SKIN_TONE] WARNING: Weights not found at {MODEL_PATH}", file=sys.stderr, flush=True)
        
        m.eval()
        _model = m
        print("[SKIN_TONE] ✓ Model READY", file=sys.stderr, flush=True)
        return _model
    except Exception as e:
        _model_load_error = str(e)
        print(f"[SKIN_TONE] FATAL: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return None

# Eager load at import time
print("[SKIN_TONE] Attempting eager load at import...", file=sys.stderr, flush=True)
_load_model()

_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

def predict_skin_tone(img: Image.Image) -> str:
    try:
        if _model is None:
            print(f"[SKIN_TONE] ERROR: Model not loaded. Error was: {_model_load_error}", file=sys.stderr, flush=True)
            return "Unknown"
        
        width, height = img.size
        cropped = img.crop((int(width * 0.2), 0, int(width * 0.8), int(height * 0.4)))

        print(f"[SKIN_TONE] Predicting... Original: {img.size}, Cropped: {cropped.size}", file=sys.stderr, flush=True)

        tensor = _transform(cropped).unsqueeze(0)
        with torch.no_grad():
            logits = _model(tensor)
            idx = logits.argmax(1).item()
        result = CLASSES[idx]
        print(f"[SKIN_TONE] ✓ {result}", file=sys.stderr, flush=True)
        return result
    except Exception as e:
        print(f"[SKIN_TONE] Prediction error: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return "Unknown"