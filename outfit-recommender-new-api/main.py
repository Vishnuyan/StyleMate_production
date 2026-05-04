import os
import random
import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
import sys
import pickle
import numpy as np


from accessories.routes import wardrobe
from accessories.routes import accessories
from outfit.outfit_recommendation_api import router as outfit_router

from contextlib import asynccontextmanager

from smart_wardrobe.routes import (
    upload_routes,
    recommendation_routes,
    trip_routes,
    group_routes
)

from smart_wardrobe.utils.vector_db import load_vectors_from_db

# Setup logging first
logger = logging.getLogger("stylemate-api")
logging.basicConfig(level=logging.INFO)

# ═════════════════════════════════════════════════════════
# NumPy Compatibility Module Stubs
# ═════════════════════════════════════════════════════════
# Create fake modules to intercept numpy._core imports from pickles
import types

class NumpyCompatibilityModule(types.ModuleType):
    """A module that redirects missing attributes to numpy."""
    
    def __getattr__(self, name):
        # Try to get from numpy first
        try:
            return getattr(np, name)
        except AttributeError:
            pass
        
        # Try to get from numpy.core.multiarray (which is numpy in newer versions)
        try:
            return getattr(np.core if hasattr(np, 'core') else np, name)
        except AttributeError:
            pass
        
        # Return a placeholder for unknown attributes
        return super().__getattr__(name)

# Create numpy._core stub
if 'numpy._core' not in sys.modules:
    numpy_core = NumpyCompatibilityModule('numpy._core')
    numpy_core_multiarray = NumpyCompatibilityModule('numpy._core.multiarray')
    numpy_core_umath = NumpyCompatibilityModule('numpy._core.umath')
    
    sys.modules['numpy._core'] = numpy_core
    sys.modules['numpy._core.multiarray'] = numpy_core_multiarray
    sys.modules['numpy._core.umath'] = numpy_core_umath
    
    # Add ndarray and other common attributes
    numpy_core_multiarray.ndarray = np.ndarray
    numpy_core_multiarray.scalar = np.generic
    numpy_core_multiarray._reconstruct = lambda subtype, shape, dtype: np.empty(shape, dtype=dtype)

# Create numpy.core stub (older versions use this)
if 'numpy.core' not in sys.modules:
    numpy_core_old = NumpyCompatibilityModule('numpy.core')
    numpy_core_multiarray_old = NumpyCompatibilityModule('numpy.core.multiarray')
    numpy_core_umath_old = NumpyCompatibilityModule('numpy.core.umath')
    
    sys.modules['numpy.core'] = numpy_core_old
    sys.modules['numpy.core.multiarray'] = numpy_core_multiarray_old
    sys.modules['numpy.core.umath'] = numpy_core_umath_old
    
    numpy_core_multiarray_old.ndarray = np.ndarray
    numpy_core_multiarray_old.scalar = np.generic
    numpy_core_multiarray_old._reconstruct = lambda subtype, shape, dtype: np.empty(shape, dtype=dtype)

import pandas as pd
import joblib
import torch
import torch.nn as nn
from torchvision import transforms, models
import tensorflow as tf
from PIL import Image
import io
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, Field
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from passlib.context import CryptContext
from jose import JWTError, jwt
import shap  # Local SHAP explanations

from accessories.routes import extract, recommend as necklace_recommend, generate, wardrobe, cache, tryon

# ─────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/stylemate")
JWT_SECRET = os.getenv("JWT_SECRET", "change-this-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading Smart Wardrobe FAISS vectors...")
    
    try:
        load_vectors_from_db()
        logger.info("Smart Wardrobe FAISS loaded successfully")
    except Exception as e:
        logger.error(f"FAISS loading failed: {e}")
    
    yield
    
    logger.info("Application shutdown")

# ─────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────
app = FastAPI(
    title="StyleMate Outfit Recommender API",
    version="7.1",
    description="Two independent rankers + local TreeSHAP explanations (no external LLM)",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173",
                   "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("generated", exist_ok=True)
app.mount("/generated", StaticFiles(directory="generated"), name="generated")

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.mount(
    "/uploaded_accessories",
    StaticFiles(directory="uploaded_accessories"),
    name="uploaded_accessories"
)

mongo_client = AsyncIOMotorClient(MONGODB_URI)
db = mongo_client["stylemate"]
users_collection = db["User"]

# ─────────────────────────────────────────────────────────
# Auth models
# ─────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    name: str = Field(..., min_length=2)

class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginCredentials(BaseModel):
    email: EmailStr
    password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    payload = {**data, "exp": datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    exc = HTTPException(status.HTTP_401_UNAUTHORIZED, "Could not validate credentials",
                        headers={"WWW-Authenticate": "Bearer"})
    try:
        uid = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM]).get("sub")
        if not uid: raise exc
    except JWTError:
        raise exc
    user = await users_collection.find_one({"_id": ObjectId(uid)})
    if not user: raise exc
    return user

# ═════════════════════════════════════════════════════════
# LOAD ARTEFACTS
# ═════════════════════════════════════════════════════════
MODEL_DIR = "model"

# Initialize as None so code can check if loaded
outfit_ranker = None
colour_ranker = None
outfit_shap_explainer = None
colour_shap_explainer = None
outfit_xai_table = None
colour_xai_table = None
le_body = None
le_skin = None
le_cat = None
le_outfit = None
le_colour = None
OUTFIT_FEATURES = None
COLOUR_FEATURES = None
ALL_OUTFITS = None
ALL_COLOURS = None

try:
    try:
        outfit_ranker = joblib.load(os.path.join(MODEL_DIR, "model_outfit_ranker.pkl"))
        colour_ranker = joblib.load(os.path.join(MODEL_DIR, "model_colour_ranker.pkl"))
        logger.info("✓ Outfit and colour rankers loaded")
    except Exception as e:
        logger.warning(f"Could not load rankers: {e}")
    
    try:
        # SHAP explainers (local TreeSHAP)
        outfit_shap_explainer = joblib.load(os.path.join(MODEL_DIR, "shap_explainer_outfit.pkl"))
        colour_shap_explainer = joblib.load(os.path.join(MODEL_DIR, "shap_explainer_colour.pkl"))
        logger.info("✓ SHAP explainers loaded")
    except Exception as e:
        logger.warning(f"Could not load SHAP explainers: {e}")
    
    try:
        # Precomputed mean component tables
        outfit_xai_table = joblib.load(os.path.join(MODEL_DIR, "outfit_xai_table.pkl"))
        colour_xai_table = joblib.load(os.path.join(MODEL_DIR, "colour_xai_table.pkl"))
        logger.info("✓ XAI tables loaded")
    except Exception as e:
        logger.warning(f"Could not load XAI tables: {e}")
    
    try:
        le_body    = joblib.load(os.path.join(MODEL_DIR, "encoder_body.pkl"))
        le_skin    = joblib.load(os.path.join(MODEL_DIR, "encoder_skin.pkl"))
        le_cat     = joblib.load(os.path.join(MODEL_DIR, "encoder_category.pkl"))
        le_outfit  = joblib.load(os.path.join(MODEL_DIR, "encoder_outfit.pkl"))
        le_colour  = joblib.load(os.path.join(MODEL_DIR, "encoder_colour.pkl"))
        logger.info("✓ Encoders loaded")
    except Exception as e:
        logger.warning(f"Could not load encoders: {e}")
    
    try:
        OUTFIT_FEATURES  = joblib.load(os.path.join(MODEL_DIR, "outfit_feature_names.pkl"))
        COLOUR_FEATURES  = joblib.load(os.path.join(MODEL_DIR, "colour_feature_names.pkl"))
        logger.info("✓ Feature names loaded")
    except Exception as e:
        logger.warning(f"Could not load feature names: {e}")
    
    try:
        ALL_OUTFITS  = joblib.load(os.path.join(MODEL_DIR, "outfit_catalogue.pkl"))
        ALL_COLOURS  = joblib.load(os.path.join(MODEL_DIR, "colour_catalogue.pkl"))
        logger.info("✓ Catalogues loaded")
    except Exception as e:
        logger.warning(f"Could not load catalogues: {e}")
    
    if all([outfit_ranker, colour_ranker, outfit_shap_explainer, colour_shap_explainer]):
        logger.info(f"✓ Artefacts loaded successfully")
    else:
        logger.warning("Some artefacts could not be loaded - functionality may be limited")
        
except Exception as e:
    logger.error(f"Critical error loading artefacts: {e}")

# Pre-index XAI tables (if loaded)
if outfit_xai_table is not None:
    try:
        outfit_xai_index = outfit_xai_table.set_index(["body_shape", "category", "outfit_type"])
        colour_xai_index = colour_xai_table.set_index(["skin_tone", "colour_family"])
        logger.info("✓ XAI indices created")
    except Exception as e:
        logger.warning(f"Could not create XAI indices: {e}")
        outfit_xai_index = None
        colour_xai_index = None
else:
    outfit_xai_index = None
    colour_xai_index = None

if ALL_OUTFITS is not None and ALL_COLOURS is not None:
    logger.info(f"✓ Artefacts ready | outfits={len(ALL_OUTFITS)} | colours={len(ALL_COLOURS)}")

# ─────────────────────────────────────────────────────────
# BODY SHAPE MODEL (PyTorch EfficientNet-B3)
# ─────────────────────────────────────────────────────────
BODY_MODEL_PATH = "EfficientNet-B3_best_model.pth"
BODY_SHAPES = ["apple", "hourglass", "inverted_triangle", "pear", "rectangle"]
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

try:
    body_model = models.efficientnet_b3(weights=None)
    in_f = body_model.classifier[1].in_features
    body_model.classifier[1] = nn.Sequential(nn.Dropout(0.5), nn.Linear(in_f, len(BODY_SHAPES)))
    body_model.load_state_dict(torch.load(BODY_MODEL_PATH, map_location=device))
    body_model.to(device).eval()
    logger.info("Body shape model loaded")
except Exception as e:
    logger.critical(f"Body model failed: {e}")
    raise

body_transform = transforms.Compose([
    transforms.Resize((300, 300)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

# ─────────────────────────────────────────────────────────
# SKIN TONE MODEL (TensorFlow / Keras)
# ─────────────────────────────────────────────────────────
SKIN_MODEL_PATH = "efficientnetB3_skin_tone_4class_v2.keras"
SKIN_CLASSES = ["dark", "light", "mid-dark", "mid-light"]

try:
    skin_model = tf.keras.models.load_model(SKIN_MODEL_PATH)
    logger.info("Skin tone model loaded")
except Exception as e:
    logger.critical(f"Skin model failed: {e}")
    raise

def preprocess_skin(img: Image.Image) -> np.ndarray:
    arr = np.expand_dims(np.array(img.convert("RGB").resize((300, 300))), axis=0)
    return tf.keras.applications.efficientnet.preprocess_input(arr)

# ─────────────────────────────────────────────────────────
# COLOUR SWATCHES
# ─────────────────────────────────────────────────────────
COLOUR_SWATCHES: dict[str, list[str]] = {
    "jewel tones": ["sapphire", "emerald", "amethyst", "ruby", "deep teal", "royal purple"],
    "earth tones": ["olive", "rust", "terracotta", "camel", "burnt sienna", "tan"],
    "neutral tones": ["navy", "black", "charcoal", "cream", "stone", "beige"],
    "rich darks": ["burgundy", "plum", "forest green", "midnight blue", "oxblood"],
    "pastel tones": ["lavender", "mint", "powder blue", "baby pink", "pale lilac", "peach"],
    "soft neutrals": ["ivory", "taupe", "champagne", "oat", "sand", "soft beige"],
    "warm brights": ["coral", "amber", "mustard", "copper", "gold", "sunset orange"],
    "cool brights": ["cobalt", "teal", "turquoise", "electric blue", "aqua", "sky blue"],
    "metallic tones": ["silver", "gold", "bronze", "rose gold", "platinum"],
    "monochrome": ["black", "white", "charcoal", "graphite", "ash grey"],
    "fresh pops": ["lime", "lemon yellow", "tangerine", "bubblegum pink", "aqua green"],
    "blush & rose": ["rose pink", "dusty pink", "mauve", "soft rose", "blush pink"],
}

# ─────────────────────────────────────────────────────────
# PATTERN RULES
# ─────────────────────────────────────────────────────────
PATTERN_RULES: dict[tuple, list[str]] = {
    ("apple", "casual"): ["vertical stripe", "solid", "small print"],
    ("apple", "formal"): ["solid", "subtle geometric"],
    ("apple", "party"): ["solid", "small print", "subtle geometric"],
    ("pear", "casual"): ["floral", "vertical stripe", "solid"],
    ("pear", "formal"): ["solid", "subtle geometric"],
    ("pear", "party"): ["floral", "small print", "solid"],
    ("hourglass", "casual"): ["solid", "floral", "small print"],
    ("hourglass", "formal"): ["solid", "subtle geometric"],
    ("hourglass", "party"): ["solid", "small print", "floral"],
    ("rectangle", "casual"): ["floral", "vertical stripe", "bold print"],
    ("rectangle", "formal"): ["solid", "subtle geometric"],
    ("rectangle", "party"): ["bold print", "floral", "small print"],
    ("inverted_triangle", "casual"): ["solid", "small print", "floral"],
    ("inverted_triangle", "formal"): ["solid", "subtle geometric"],
    ("inverted_triangle", "party"): ["solid", "small print", "floral"],
}

# def get_pattern(body: str, category: str) -> str:
#     return PATTERN_RULES.get((body, category), ["solid"])[0]

def get_pattern(body: str, category: str) -> str:
    patterns = PATTERN_RULES.get((body, category), ["solid"])

    # reduce chance of solid pattern
    weights = []
    for p in patterns:
        if p == "solid":
            weights.append(0.2)   # lower chance
        else:
            weights.append(0.4)   # higher chance

    return random.choices(patterns, weights=weights)[0]

# ═════════════════════════════════════════════════════════
# OUTFIT & COLOUR RANKING
# ═════════════════════════════════════════════════════════
# def rank_and_sample_outfit(body: str, category: str, top_k: int = 4, deterministic: bool = False):
#     # Check if ranker is available
#     if outfit_ranker is None:
#         logger.warning("Outfit ranker unavailable - using fallback recommendation")
#         # Fallback: Return random outfit from catalogue
#         outfit = np.random.choice(ALL_OUTFITS)
#         ranked_list = [{"outfit": o, "score": 0.5, "rank": i+1, "fallback": True} 
#                        for i, o in enumerate(ALL_OUTFITS)]
#         return outfit, 0.5, ranked_list
    
#     b = int(le_body.transform([body])[0])
#     c = int(le_cat.transform([category])[0])
#     rows = pd.DataFrame(
#         [[b, c, int(le_outfit.transform([o])[0])] for o in ALL_OUTFITS],
#         columns=OUTFIT_FEATURES,
#     )
#     scores = outfit_ranker.predict(rows)
#     ranked = sorted(zip(ALL_OUTFITS, scores.tolist()), key=lambda x: x[1], reverse=True)
#     ranked_list = [{"outfit": o, "score": round(sc, 4), "rank": i+1}
#                    for i, (o, sc) in enumerate(ranked)]
    
#     if deterministic:
#         return ranked[0][0], round(ranked[0][1], 4), ranked_list
    
#     top = ranked[:top_k]
#     names, sc_vals = zip(*top)
#     sc_arr = np.array(sc_vals) - min(sc_vals) + 0.01
#     probs = sc_arr / sc_arr.sum()
#     idx = int(np.random.choice(len(names), p=probs))
#     return names[idx], round(float(sc_vals[idx]), 4), ranked_list
def rank_and_sample_outfit(body: str, category: str, top_k: int = 6, deterministic: bool = False):
    # Check if ranker is available
    if outfit_ranker is None:
        logger.warning("Outfit ranker unavailable - using fallback recommendation")

        outfit = np.random.choice(ALL_OUTFITS)
        ranked_list = [
            {
                "outfit": o,
                "score": 0.5,
                "rank": i + 1,
                "fallback": True
            }
            for i, o in enumerate(ALL_OUTFITS)
        ]
        return outfit, 0.5, ranked_list

    b = int(le_body.transform([body])[0])
    c = int(le_cat.transform([category])[0])

    rows = pd.DataFrame(
        [[b, c, int(le_outfit.transform([o])[0])] for o in ALL_OUTFITS],
        columns=OUTFIT_FEATURES,
    )

    scores = outfit_ranker.predict(rows)

    ranked = sorted(
        zip(ALL_OUTFITS, scores.tolist()),
        key=lambda x: x[1],
        reverse=True
    )

    ranked_list = [
        {
            "outfit": o,
            "score": round(sc, 4),
            "rank": i + 1
        }
        for i, (o, sc) in enumerate(ranked)
    ]

    # deterministic mode → always pick best
    if deterministic:
        return ranked[0][0], round(ranked[0][1], 4), ranked_list

    # NEW SAMPLING LOGIC
    top = ranked[:top_k]
    names, sc_vals = zip(*top)

    # Temperature scaling for diversity
    temperature = 2.0
    sc_arr = np.exp(np.array(sc_vals) / temperature)
    probs = sc_arr / sc_arr.sum()

    idx = int(np.random.choice(len(names), p=probs))

    return names[idx], round(float(sc_vals[idx]), 4), ranked_list

def rank_and_sample_colour(skin: str, top_k: int = 3):
    # Check if ranker is available
    if colour_ranker is None:
        logger.warning("Colour ranker unavailable - using fallback recommendation")
        # Fallback: Return random colour
        chosen = np.random.choice(ALL_COLOURS)
        pool = COLOUR_SWATCHES.get(chosen, ["black"])
        swatches = random.sample(pool, min(3, len(pool)))
        colour_ranking = [{"colour_family": c, "score": 0.5, "rank": i+1, "fallback": True}
                          for i, c in enumerate(ALL_COLOURS)]
        return chosen, swatches, colour_ranking
    
    s = int(le_skin.transform([skin])[0])
    rows = pd.DataFrame(
        [[s, int(le_colour.transform([c])[0])] for c in ALL_COLOURS],
        columns=COLOUR_FEATURES,
    )
    scores = colour_ranker.predict(rows)
    ranked = sorted(zip(ALL_COLOURS, scores.tolist()), key=lambda x: x[1], reverse=True)
    colour_ranking = [{"colour_family": c, "score": round(sc, 4), "rank": i+1}
                      for i, (c, sc) in enumerate(ranked)]
    
    top = ranked[:top_k]
    names, sc_vals = zip(*top)
    sc_arr = np.array(sc_vals) - min(sc_vals) + 0.01
    probs = sc_arr / sc_arr.sum()
    chosen = names[int(np.random.choice(len(names), p=probs))]
    pool = COLOUR_SWATCHES.get(chosen, ["black"])
    swatches = random.sample(pool, min(3, len(pool)))
    return chosen, swatches, colour_ranking

# ═════════════════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════════════════
def parse_outfit(outfit_type: str) -> dict:
    if " | " in outfit_type:
        upper, lower = outfit_type.split(" | ", 1)
        return {"is_single_piece": False, "upper_wear": upper.strip(),
                "lower_wear": lower.strip()}
    return {"is_single_piece": True, "upper_wear": None, "lower_wear": None}

def fetch_xai_data(body: str, skin: str, category: str, outfit: str, colour_family: str) -> dict:
    try:
        if outfit_xai_index is not None:
            orow = outfit_xai_index.loc[(body, category, outfit)]
            sil_val = round(float(orow["silhouette_contribution"]), 3)
            pat_val = round(float(orow["pattern_contribution"]), 3)
            pb_val  = round(float(orow["piece_bonus"]), 3)
            out_score = round(float(orow["mean_score"]), 3)
            sil_tier = str(orow["silhouette_tier"])
            pat_tier = str(orow["pattern_tier"])
        else:
            sil_val = pat_val = pb_val = out_score = 0.0
            sil_tier = pat_tier = "neutral"
    except:
        sil_val = pat_val = pb_val = out_score = 0.0
        sil_tier = pat_tier = "neutral"

    try:
        if colour_xai_index is not None:
            crow = colour_xai_index.loc[(skin, colour_family)]
            col_val = round(float(crow["colour_contribution"]), 3)
            col_tier = str(crow["colour_tier"])
        else:
            col_val = 0.0
            col_tier = "neutral"
    except:
        col_val = 0.0
        col_tier = "neutral"

    return {
        "silhouette_score": sil_val,
        "silhouette_tier": sil_tier,
        "pattern_score": pat_val,
        "pattern_tier": pat_tier,
        "piece_bonus": pb_val,
        "colour_score": col_val,
        "colour_tier": col_tier,
        "outfit_mean_score": out_score,
    }

# ═════════════════════════════════════════════════════════
# FRIENDLY STYLIST EXPLANATION (SHAP-aware, no numbers shown)
# ═════════════════════════════════════════════════════════
def generate_friendly_explanation(
    body: str,
    skin: str,
    category: str,
    outfit: str,
    colour_family: str,
    pattern: str,
    xai_data: dict,
    shap_out: list[float],
    shap_col: list[float],
    is_single_piece: bool,
    recommended_colours: list[str],
) -> str:
    piece_desc = "single-piece dress" if is_single_piece else "two-piece outfit"
    outfit_name = outfit.replace(" | ", " with ")

    # Body & outfit strength
    body_contrib, cat_contrib, outfit_contrib = shap_out
    silhouette_strength = xai_data["silhouette_score"]

    if silhouette_strength > 0.25:
        body_strength = "really flatters"
        emphasis = "especially"
    elif silhouette_strength > 0.10:
        body_strength = "nicely flatters"
        emphasis = "particularly"
    elif silhouette_strength > -0.05:
        body_strength = "works well for"
        emphasis = ""
    else:
        body_strength = "can work nicely for"
        emphasis = "and we chose it because"

    body_praise = {
        "hourglass": f"beautifully defines your waist and balances your curves",
        "pear": f"balances your proportions by adding harmony up top and skimming the hips",
        "apple": f"flows gracefully and keeps things comfortable around the midsection",
        "rectangle": f"adds beautiful shape and creates the illusion of curves",
        "inverted_triangle": f"softens the shoulders and creates a more balanced, feminine silhouette",
    }.get(body, "flatters your natural shape")

    # Colour strength
    colour_contrib = shap_col[1]
    colour_harmony = xai_data["colour_score"]

    if colour_harmony > 0.15:
        colour_adj = "absolutely stunning"
        colour_why = "they bring out your natural glow and look incredibly rich"
    elif colour_harmony > 0.05:
        colour_adj = "very flattering"
        colour_why = "they complement your undertones beautifully"
    else:
        colour_adj = "a solid, elegant match"
        colour_why = "they keep things polished and sophisticated"

    # Pattern wording
    pattern_strength = xai_data["pattern_score"]
    if pattern_strength > 0.08:
        pattern_adj = "adds just the right touch of personality"
    elif pattern_strength > -0.03:
        pattern_adj = "keeps the look clean and timeless"
    else:
        pattern_adj = "keeps everything sleek and distraction-free"

    # Final explanation
    explanation = f"""
For your {body} figure and a {category} occasion, the {outfit_name} ({piece_desc}) is a wonderful pick.

The silhouette {body_strength} your shape — {emphasis} the way it {body_praise}.  
That's exactly why this style feels so right for you right now.

On the colour side, {colour_family} tones are {colour_adj} with your {skin} skin tone.  
{colour_why}, giving you that polished, confident vibe.

We paired it with a {pattern} pattern because it {pattern_adj}, letting the cut and colours really shine.

This combination gives structure where it flatters, elegance where it counts, and a look that feels completely you.
    """.strip()

    return explanation

# ═════════════════════════════════════════════════════════
# AUTH ENDPOINTS
# ═════════════════════════════════════════════════════════
@app.post("/api/auth/signup", response_model=UserOut)
async def signup(user: UserCreate):
    if await users_collection.find_one({"email": user.email}):
        raise HTTPException(400, "Email already registered")
    result = await users_collection.insert_one({
        "email": user.email, "name": user.name,
        "password": pwd_context.hash(user.password),
        "createdAt": datetime.utcnow(),
    })
    created = await users_collection.find_one({"_id": result.inserted_id})
    return UserOut(id=str(created["_id"]), email=created["email"], name=created["name"])

@app.post("/api/auth/login", response_model=Token)
async def login(creds: LoginCredentials):
    user = await users_collection.find_one({"email": creds.email})
    if not user or not pwd_context.verify(creds.password, user["password"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password",
                            headers={"WWW-Authenticate": "Bearer"})
    token = create_access_token({"sub": str(user["_id"])},
                                timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": str(user["_id"]), "email": user["email"], "name": user["name"]}
    }

# ═════════════════════════════════════════════════════════
# RECOMMENDATION ENDPOINT
# ═════════════════════════════════════════════════════════
@app.post("/api/recommend")
async def recommend(
    body_image: UploadFile = File(...),
    skin_image: UploadFile = File(...),
    category: str = Form(...),
    consistency_mode: bool = Form(default=False),
):
    if category not in {"casual", "formal", "party"}:
        raise HTTPException(422, "category must be casual, formal, or party")

    # 1. Body shape prediction
    try:
        pil = Image.open(io.BytesIO(await body_image.read())).convert("RGB")
        tensor = body_transform(pil).unsqueeze(0).to(device)
        with torch.no_grad():
            probs = torch.softmax(body_model(tensor), dim=1)[0]
        body_pred = BODY_SHAPES[probs.argmax().item()]
        body_conf = round(float(probs.max().item()), 3)
    except Exception as e:
        logger.error(f"Body prediction failed: {e}", exc_info=True)
        raise HTTPException(400, "Could not process body image")

    # 2. Skin tone prediction
    try:
        pil2 = Image.open(io.BytesIO(await skin_image.read())).convert("RGB")
        arr = preprocess_skin(pil2)
        skin_probs = skin_model.predict(arr, verbose=0)[0]
        skin_pred = SKIN_CLASSES[int(np.argmax(skin_probs))]
        skin_conf = round(float(np.max(skin_probs)), 3)
    except Exception as e:
        logger.error(f"Skin prediction failed: {e}", exc_info=True)
        raise HTTPException(400, "Could not process skin image")

    # 3. Rank & sample outfit
    try:
        outfit, outfit_score, outfit_ranking = rank_and_sample_outfit(
            body_pred, category, top_k=6, deterministic=consistency_mode
        )
        outfit_info = parse_outfit(outfit)
    except Exception as e:
        logger.error(f"Outfit ranking failed: {e}", exc_info=True)
        raise HTTPException(503, {"error": "Outfit ranking unavailable", "details": str(e)})

    top5_alternatives = [
        item for item in outfit_ranking[:6] if item["outfit"] != outfit
    ][:5]

    # 4. Rank & sample colour
    try:
        colour_family, swatches, colour_ranking = rank_and_sample_colour(skin_pred, top_k=3)
    except Exception as e:
        logger.error(f"Colour ranking failed: {e}", exc_info=True)
        raise HTTPException(503, {"error": "Colour ranking unavailable", "details": str(e)})
        colour_family, swatches, colour_ranking = "neutral tones", ["black", "white", "grey"], []

    # 5. Pattern
    pattern = get_pattern(body_pred, category)

    # 6. Fetch real component values
    xai_data = fetch_xai_data(body_pred, skin_pred, category, outfit, colour_family)

    # 7. Compute SHAP values (with fallback for unavailable explainers)
    b = int(le_body.transform([body_pred])[0])
    c = int(le_cat.transform([category])[0])
    o = int(le_outfit.transform([outfit])[0])
    row_out = pd.DataFrame([[b, c, o]], columns=OUTFIT_FEATURES)
    
    if outfit_shap_explainer is not None:
        shap_out = outfit_shap_explainer.shap_values(row_out)[0]
    else:
        logger.warning("Outfit SHAP explainer unavailable - using default feature importance")
        # Default neutral SHAP values when explainer is unavailable
        shap_out = np.array([0.0, 0.0, 0.0])

    s = int(le_skin.transform([skin_pred])[0])
    cf = int(le_colour.transform([colour_family])[0])
    row_col = pd.DataFrame([[s, cf]], columns=COLOUR_FEATURES)
    
    if colour_shap_explainer is not None:
        shap_col = colour_shap_explainer.shap_values(row_col)[0]
    else:
        logger.warning("Colour SHAP explainer unavailable - using default feature importance")
        # Default neutral SHAP values when explainer is unavailable
        shap_col = np.array([0.0, 0.0])

    # 8. Generate friendly explanation
    explanation = generate_friendly_explanation(
        body=body_pred,
        skin=skin_pred,
        category=category,
        outfit=outfit,
        colour_family=colour_family,
        pattern=pattern,
        xai_data=xai_data,
        shap_out=shap_out.tolist(),
        shap_col=shap_col.tolist(),
        is_single_piece=outfit_info["is_single_piece"],
        recommended_colours=swatches
    )

    # 9. Outfit summary sentence
    colour_str = ", ".join(swatches)
    if outfit_info["is_single_piece"]:
        outfit_summary = (
            f"Wear a {outfit} in {colour_str} tones with a {pattern} pattern "
            f"for a stylish {category} look."
        )
    else:
        outfit_summary = (
            f"Pair a {outfit_info['upper_wear']} with {outfit_info['lower_wear']} "
            f"in {colour_str} tones with a {pattern} pattern — perfect for {category}."
        )

    return JSONResponse({
        "status": "success",
        "body_shape": body_pred,
        "body_confidence": body_conf,
        "skin_tone": skin_pred,
        "skin_confidence": skin_conf,
        "category": category,
        "outfit_type": outfit,
        "is_single_piece": outfit_info["is_single_piece"],
        "upper_wear": outfit_info["upper_wear"],
        "lower_wear": outfit_info["lower_wear"],
        "outfit_score": outfit_score,
        "colour_family": colour_family,
        "recommended_colours": swatches,
        "pattern": pattern,
        "outfit_recommendation": outfit_summary,
        "why_this_recommendation": explanation,
        "score_breakdown": {
            "silhouette_fit": xai_data["silhouette_score"],
            "silhouette_tier": xai_data["silhouette_tier"],
            "colour_harmony": xai_data["colour_score"],
            "colour_tier": xai_data["colour_tier"],
            "pattern_fit": xai_data["pattern_score"],
            "pattern_tier": xai_data["pattern_tier"],
            "piece_bonus": xai_data["piece_bonus"],
            "outfit_mean_score": xai_data["outfit_mean_score"],
        },
        "top5_alternatives": top5_alternatives,
        "outfit_ranking": outfit_ranking[:10],
        "colour_ranking": colour_ranking[:6],
    })

app.include_router(extract.router,   prefix="/api/necklace")
app.include_router(necklace_recommend.router, prefix="/api/necklace")
app.include_router(generate.router,  prefix="/api/necklace")
app.include_router(wardrobe.router,  prefix="/api/necklace")
app.include_router(cache.router,     prefix="/api/necklace")
app.include_router(tryon.router,     prefix="/api/necklace")
app.include_router(wardrobe.router,  prefix="/api")
app.include_router(wardrobe.router,prefix="/api/wardrobe")
app.include_router(accessories.router,prefix="/api/accessories")
app.include_router(outfit_router,prefix="/api/outfit")

app.include_router(upload_routes.router, prefix="/upload")
app.include_router(recommendation_routes.router, prefix="/recommend")
app.include_router(trip_routes.router, prefix="/trip")
app.include_router(group_routes.router, prefix="/group")

# ═════════════════════════════════════════════════════════
# HEALTH CHECK
# ═════════════════════════════════════════════════════════
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "7.1",
        "models": {
            "body_shape": "✓ PyTorch EfficientNet-B3",
            "skin_tone": "✓ PyTorch EfficientNet-B0",
            "neckline": "✓ PyTorch EfficientNet-B0",
            "outfit_ranker": "✓ Available" if outfit_ranker else "✗ Unavailable (pickle incompatibility)",
            "colour_ranker": "✓ Available" if colour_ranker else "✗ Unavailable (pickle incompatibility)",
            "shap_explainers": "✓ Available" if outfit_shap_explainer and colour_shap_explainer else "✗ Unavailable",
        },
        "outfit_model": "HistGradientBoostingRegressor (body + category → silhouette)",
        "colour_model": "HistGradientBoostingRegressor (skin tone → colour harmony)",
        "xai_method": "Local TreeSHAP + friendly stylist explanations",
        "xai_note": "No external LLM or API calls — fully local explainability",
        "outfit_pool": len(ALL_OUTFITS) if ALL_OUTFITS else 0,
        "colour_pool": len(ALL_COLOURS) if ALL_COLOURS else 0,
        "body_shapes": BODY_SHAPES,
        "skin_tones": SKIN_CLASSES,
        "categories": ["casual", "formal", "party"],
        "note": "Ranker unavailability: Models were pickled with older NumPy. Fallback recommendations are random but functional.",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)