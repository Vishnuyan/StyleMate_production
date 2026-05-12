# 👗 StyleMate — AI-Powered Outfit Recommender

StyleMate is a full-stack AI fashion assistant that analyses your body shape and skin tone to deliver personalised outfit and colour recommendations. It combines computer vision models, a smart wardrobe management system, and an accessories advisor into a single cohesive platform.

---

## 🚀 Features

- **Body Shape Detection** — PyTorch EfficientNet-B3 model classifies body shape from an uploaded image
- **Skin Tone Detection** — TensorFlow/Keras EfficientNet-B3 model classifies skin tone into 4 categories
- **Outfit Ranking** — ML ranker (HistGradientBoosting) recommends outfits tailored to body shape + occasion
- **Colour Harmony** — Colour family ranking based on skin tone, with curated swatches
- **XAI Explanations** — Local TreeSHAP-powered, human-readable style explanations (no external LLM calls)
- **Smart Wardrobe** — Upload, categorise, and get AI-powered outfit suggestions from your own wardrobe
- **Accessories Advisor** — Necklace style matching, virtual try-on, and AI image generation via ComfyUI
- **Group Outfit Matching** — Coordinate outfits across multiple users
- **Trip Packing Planner** — Weather-aware outfit planning for trips
- **Authentication** — JWT-based signup/login on both frontend and backend

---

## 🏗️ Project Structure

```
StyleMate/
├── stylemate-backend/          # Python FastAPI backend (AI models + REST API)
│   ├── main.py                 # App entry point, model loading, core endpoints
│   ├── accessories/            # Necklace extraction, recommendation, generation
│   ├── outfit/                 # Outfit dataset API
│   ├── smart_wardrobe/         # Wardrobe upload, FAISS vector search, trip/group
│   ├── routes/                 # Shared route modules
│   ├── model/                  # Trained ML model artefacts (.pkl files)
│   ├── requirements.txt        # Python dependencies
│   └── .env.example            # Environment variable template
│
└── stylemate-frontend/         # TypeScript + React + Vite frontend
    ├── src/
    │   ├── pages/              # Route-level page components
    │   ├── components/         # Shared UI components (Header, Footer, etc.)
    │   ├── services/api.ts     # Axios client pointing to FastAPI backend
    │   └── App.tsx             # Router and protected routes
    ├── server.ts               # Express dev server with auth + recommendation routes
    ├── vite.config.ts
    └── .env.example            # Frontend environment variable template
```

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB Atlas account (or local MongoDB instance)
- (Optional) ComfyUI server for image generation

---

### Backend

```bash
cd stylemate-backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your actual API keys and MongoDB URI

# Run the FastAPI server
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

> **Note:** Large model files (`.pth`, `.keras`) are excluded from the repository due to size. You will need to supply or train your own models and place them in the backend root directory.

---

### Frontend

```bash
cd stylemate-frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Set VITE_API_BASE_URL to your backend URL

# Start the dev server
npm run dev
```

The app will be available at `http://localhost:3000`.

---

## 🔐 Environment Variables

### Backend (`stylemate-backend/.env`)

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key for accessories generation |
| `MONGODB_URI` | MongoDB Atlas connection string |
| `MONGODB_DB_NAME` | Database name (default: `stylemate`) |
| `MONGODB_COLLECTION_NAME` | Collection name (default: `wardrobe`) |
| `JWT_SECRET` | Secret key for signing JWT tokens |
| `COMFYUI_URL` | URL of a running ComfyUI instance |

### Frontend (`stylemate-frontend/.env`)

| Variable | Description |
|----------|-------------|
| `VITE_API_BASE_URL` | Base URL of the FastAPI backend |

---

## 🧠 ML Models

| Model | Framework | Purpose |
|-------|-----------|---------|
| `EfficientNet-B3_best_model.pth` | PyTorch | Body shape classification (5 classes) |
| `efficientnetB3_skin_tone_4class_v2.keras` | TensorFlow/Keras | Skin tone classification (4 classes) |
| `model/model_outfit_ranker.pkl` | scikit-learn | Outfit type ranking |
| `model/model_colour_ranker.pkl` | scikit-learn | Colour family ranking |
| `model/shap_explainer_*.pkl` | SHAP | Local TreeSHAP explanations |

> Large model files are not included in this repository. See the backend README for details on training or obtaining them.

---

## 📡 API Endpoints (Key)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/auth/signup` | Register a new user |
| `POST` | `/api/auth/login` | Login and receive JWT |
| `POST` | `/api/recommend` | Full outfit recommendation from images |
| `GET`  | `/health` | API health check |
| `POST` | `/upload/upload` | Upload wardrobe item |
| `POST` | `/recommend/pro` | AI stylist recommendation |
| `POST` | `/api/necklace/extract` | Extract necklace style from image |

Full docs available at `/docs` when the server is running.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS v4, Framer Motion |
| Backend | FastAPI, Uvicorn, Python 3.10+ |
| Database | MongoDB Atlas (Motor async driver) |
| Auth | JWT (python-jose / jsonwebtoken) + bcrypt |
| AI/ML | PyTorch, TensorFlow/Keras, scikit-learn, SHAP, FAISS |
| Image AI | ComfyUI (local), OpenAI, rembg |

---

## 📄 License

This project is for academic and portfolio purposes.
