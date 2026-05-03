import torch
import torch.nn as nn
from torchvision import models
from smart_wardrobe.core.config import MODEL_PATHS
from smart_wardrobe.models.torch_model_loader import build_classifier_from_state_dict, load_state_dict_from_path
from smart_wardrobe.utils.image_utils import preprocess_image

# Load EfficientNet model
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

# Load model
model = load_model(MODEL_PATHS["clothing"], 7)

# Labels
CLOTHING_LABELS = {
    0: "Dress",
    1: "Hoodie",
    2: "Jacket",
    3: "Pants",
    4: "Shirt",
    5: "Shorts",
    6: "Tshirt"
}

# Prediction
def predict_clothing(image_path):
    try:
        image = preprocess_image(image_path)

        with torch.no_grad():
            output = model(image)

        pred_idx = int(output.argmax())

        return CLOTHING_LABELS.get(pred_idx, "Unknown")

    except Exception as e:
        return f"Error: {str(e)}"