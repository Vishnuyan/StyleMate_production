import torch
import torch.nn as nn
import joblib
import os

MODEL_PATH    = os.path.join(os.path.dirname(__file__), "../models/recommender/recommender_model.pth")
ENCODERS_PATH = os.path.join(os.path.dirname(__file__), "../models/recommender/label_encoders.pkl")

# ── Model definition (must match train.py exactly) ────────────────────────────
class Recommender(nn.Module):
    def __init__(self, num_styles, num_metals):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(3, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
        )
        self.head_style = nn.Linear(64, num_styles)
        self.head_metal = nn.Linear(64, num_metals)

    def forward(self, x):
        feat = self.net(x)
        return self.head_style(feat), self.head_metal(feat)

# ── Load once at module import ────────────────────────────────────────────────
_model    = None
_encoders = None

def _load():
    global _model, _encoders
    if _model is not None:
        return

    if not os.path.exists(ENCODERS_PATH):
        raise FileNotFoundError(
            f"label_encoders.pkl not found at {ENCODERS_PATH}. "
            "Run train.py first to generate it."
        )

    _encoders = joblib.load(ENCODERS_PATH)
    num_styles = len(_encoders["necklace_style"].classes_)
    num_metals = len(_encoders["metal"].classes_)

    _model = Recommender(num_styles, num_metals)

    if os.path.exists(MODEL_PATH):
        _model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
        print("Recommender model loaded.")
    else:
        print("WARNING: recommender_model.pth not found — using untrained model")

    _model.eval()

# ── Inference ─────────────────────────────────────────────────────────────────
def predict_recommendation(skin_tone: str, neckline: str, dress_color: str) -> dict:
    _load()

    # Encode inputs
    skin_enc  = _encoders["skin_tone"].transform([skin_tone])[0]
    neck_enc  = _encoders["neckline"].transform([neckline])[0]
    color_enc = _encoders["dress_color"].transform([dress_color])[0]

    X = torch.tensor([[skin_enc, neck_enc, color_enc]], dtype=torch.float32)

    with torch.no_grad():
        s_pred, m_pred = _model(X)
        style_idx = s_pred.argmax(1).item()
        metal_idx = m_pred.argmax(1).item()

    necklace_style = _encoders["necklace_style"].inverse_transform([style_idx])[0]
    metal          = _encoders["metal"].inverse_transform([metal_idx])[0]

    return {
        "necklace_style": necklace_style,
        "metal":          metal,
        "input": {
            "skin_tone":   skin_tone,
            "neckline":    neckline,
            "dress_color": dress_color,
        }
    }