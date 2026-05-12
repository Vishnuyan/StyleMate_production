import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

MODEL_PATHS = {
    "clothing": os.path.join(BASE_DIR, "models_store/clothing/best_clothing_model.pth"),
    "fabric": os.path.join(BASE_DIR, "models_store/fabric/best_fabric_model_finetuned.pth"),
    "color": os.path.join(BASE_DIR, "models_store/color/best_color_model_advanced.pth"),
}

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")