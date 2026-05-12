import torch
import torch.nn as nn
from torchvision import models
from smart_wardrobe.core.config import MODEL_PATHS
from smart_wardrobe.models.torch_model_loader import build_classifier_from_state_dict, load_state_dict_from_path
from smart_wardrobe.utils.image_utils import preprocess_image

def load_model(path, num_classes):
    state_dict = load_state_dict_from_path(path, map_location="cpu")

    model = models.efficientnet_b0(weights=None)
    classifier = build_classifier_from_state_dict(state_dict, expected_num_classes=num_classes)
    if classifier is not None:
        model.classifier = classifier
    else:
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)

    model.load_state_dict(state_dict)

    model.eval()
    return model

model = load_model(MODEL_PATHS["color"], 10)

COLOR_LABELS = {
    0: "Black",
    1: "Blue",
    2: "Brown",
    3: "Green",
    4: "Grey",
    5: "Orange",
    6: "Pink",
    7: "Red",
    8: "White",
    9: "Yellow"
}

def predict_color(image_path):
    try:
        image = preprocess_image(image_path)

        with torch.no_grad():
            output = model(image)

        pred_idx = int(output.argmax())

        return COLOR_LABELS.get(pred_idx, "Unknown")

    except Exception as e:
        return f"Error: {str(e)}"