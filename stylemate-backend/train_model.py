import os
import numpy as np
import pandas as pd
import joblib
import shap
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error

# ─────────────────────────────────────────────────────────
# PART 1 — OUTFIT RANKER
# ─────────────────────────────────────────────────────────
print("=" * 60)
print("PART 1 — OUTFIT RANKER (SHAP-ready)")
print("=" * 60)

outfit_df = pd.read_csv("outfit_dataset.csv")
print(f"Loaded outfit_dataset.csv -> {len(outfit_df):,} rows")

le_body    = LabelEncoder()
le_cat     = LabelEncoder()
le_outfit  = LabelEncoder()

outfit_df["body_enc"]   = le_body.fit_transform(outfit_df["body_shape"])
outfit_df["cat_enc"]    = le_cat.fit_transform(outfit_df["category"])
outfit_df["outfit_enc"] = le_outfit.fit_transform(outfit_df["outfit_type"])

ALL_OUTFITS = list(le_outfit.classes_)
OUTFIT_FEATURES = ["body_enc", "cat_enc", "outfit_enc"]

X_out = outfit_df[OUTFIT_FEATURES]
y_out = outfit_df["silhouette_component"]

strat_out = (
    outfit_df["body_enc"].astype(str) + "_" +
    outfit_df["cat_enc"].astype(str) + "_" +
    outfit_df["outfit_enc"].astype(str)
)

X_out_tr, X_out_te, y_out_tr, y_out_te = train_test_split(
    X_out, y_out, test_size=0.2, random_state=42, stratify=strat_out
)

print(f"Train: {len(X_out_tr):,} | Test: {len(X_out_te):,}")
print(f"Target range: {y_out.min():.3f} -> {y_out.max():.3f} (spread = {y_out.max()-y_out.min():.3f})")

outfit_ranker = HistGradientBoostingRegressor(
    max_iter=600,
    max_depth=6,
    learning_rate=0.05,
    min_samples_leaf=15,
    l2_regularization=0.1,
    random_state=42,
    early_stopping=True,
    validation_fraction=0.1,
    n_iter_no_change=40,
)

outfit_ranker.fit(X_out_tr, y_out_tr)
print(f"Stopped at iteration {outfit_ranker.n_iter_}")

out_preds = outfit_ranker.predict(X_out_te)
r2_out  = r2_score(y_out_te, out_preds)
mae_out = mean_absolute_error(y_out_te, out_preds)

print(f" {'OK' if r2_out >= 0.85 else 'FAIL'} R2 : {r2_out:.4f} ({r2_out*100:.1f}%)")
print(f" MAE : {mae_out:.4f}")

# ── NDCG@3 ────────────────────────────────────────────────────────────────
outfit_means = (
    outfit_df.groupby(["body_enc", "cat_enc", "outfit_enc"])
             .agg(true_score=("score", "mean"))
             .reset_index()
)
outfit_means["pred_score"] = outfit_ranker.predict(outfit_means[OUTFIT_FEATURES])

def ndcg_at_k(df_in, k=3):
    scores = []
    for _, g in df_in.groupby(["body_enc", "cat_enc"]):
        if len(g) < k: continue
        top_idx = np.argsort(g["pred_score"].values)[::-1][:k]
        rel = g["true_score"].values[top_idx]
        dcg = sum(r / np.log2(i+2) for i, r in enumerate(rel))
        irel = np.sort(g["true_score"].values)[::-1][:k]
        idcg = sum(r / np.log2(i+2) for i, r in enumerate(irel))
        if idcg > 0:
            scores.append(dcg / idcg)
    return np.mean(scores) if scores else 0.0

ndcg3 = ndcg_at_k(outfit_means, k=3)
print(f" {'OK' if ndcg3 >= 0.95 else 'CHECK'} NDCG@3: {ndcg3:.4f}")

# ── SHAP Explainer (very important!) ──────────────────────────────────────
print("Creating Outfit SHAP TreeExplainer...")
explainer_outfit = shap.TreeExplainer(outfit_ranker)

# ─────────────────────────────────────────────────────────
# PART 2 — COLOUR RANKER
# ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("PART 2 — COLOUR RANKER (SHAP-ready)")
print("=" * 60)

colour_df = pd.read_csv("colour_dataset.csv")
print(f"Loaded colour_dataset.csv -> {len(colour_df):,} rows")

le_skin   = LabelEncoder()
le_colour = LabelEncoder()

colour_df["skin_enc"]   = le_skin.fit_transform(colour_df["skin_tone"])
colour_df["colour_enc"] = le_colour.fit_transform(colour_df["colour_family"])

ALL_COLOURS = list(le_colour.classes_)
COLOUR_FEATURES = ["skin_enc", "colour_enc"]

X_col = colour_df[COLOUR_FEATURES]
y_col = colour_df["colour_component"]

strat_col = colour_df["skin_enc"].astype(str) + "_" + colour_df["colour_enc"].astype(str)

X_col_tr, X_col_te, y_col_tr, y_col_te = train_test_split(
    X_col, y_col, test_size=0.2, random_state=42, stratify=strat_col
)

colour_ranker = HistGradientBoostingRegressor(
    max_iter=400,
    max_depth=5,
    learning_rate=0.05,
    min_samples_leaf=15,
    l2_regularization=0.1,
    random_state=42,
    early_stopping=True,
    validation_fraction=0.1,
    n_iter_no_change=30,
)

colour_ranker.fit(X_col_tr, y_col_tr)
print(f"Stopped at iteration {colour_ranker.n_iter_}")

col_preds = colour_ranker.predict(X_col_te)
r2_col  = r2_score(y_col_te, col_preds)
mae_col = mean_absolute_error(y_col_te, col_preds)

print(f" {'OK' if r2_col >= 0.85 else 'FAIL'} R2 : {r2_col:.4f} ({r2_col*100:.1f}%)")
print(f" MAE : {mae_col:.4f}")

# ── SHAP Explainer ────────────────────────────────────────────────────────
print("Creating Colour SHAP TreeExplainer...")
explainer_colour = shap.TreeExplainer(colour_ranker)

# ─────────────────────────────────────────────────────────
# XAI mean tables (still useful for components + tiers)
# ─────────────────────────────────────────────────────────
outfit_xai = (
    outfit_df.groupby(["body_shape", "category", "outfit_type"])
             .agg(
                 mean_score=("score", "mean"),
                 silhouette_contribution=("silhouette_component", "mean"),
                 pattern_contribution=("pattern_component", "mean"),
                 piece_bonus=("piece_bonus", "mean"),
                 silhouette_tier=("silhouette_tier", "first"),
                 pattern_tier=("pattern_tier", "first"),
             )
             .reset_index()
)

colour_xai = (
    colour_df.groupby(["skin_tone", "colour_family"])
             .agg(
                 mean_score=("score", "mean"),
                 colour_contribution=("colour_component", "mean"),
                 colour_tier=("colour_tier", "first"),
             )
             .reset_index()
)

# ─────────────────────────────────────────────────────────
# SAVE EVERYTHING
# ─────────────────────────────────────────────────────────
save_dir = "model"
os.makedirs(save_dir, exist_ok=True)

joblib.dump(outfit_ranker,       os.path.join(save_dir, "model_outfit_ranker.pkl"))
joblib.dump(colour_ranker,       os.path.join(save_dir, "model_colour_ranker.pkl"))

# ── Crucial: save the SHAP explainers ─────────────────────────────────────
joblib.dump(explainer_outfit,    os.path.join(save_dir, "shap_explainer_outfit.pkl"))
joblib.dump(explainer_colour,    os.path.join(save_dir, "shap_explainer_colour.pkl"))

# ── Other files (encoders, catalogues, mean tables) ───────────────────────
joblib.dump(outfit_xai,          os.path.join(save_dir, "outfit_xai_table.pkl"))
joblib.dump(colour_xai,          os.path.join(save_dir, "colour_xai_table.pkl"))

joblib.dump(le_body,             os.path.join(save_dir, "encoder_body.pkl"))
joblib.dump(le_skin,             os.path.join(save_dir, "encoder_skin.pkl"))
joblib.dump(le_cat,              os.path.join(save_dir, "encoder_category.pkl"))
joblib.dump(le_outfit,           os.path.join(save_dir, "encoder_outfit.pkl"))
joblib.dump(le_colour,           os.path.join(save_dir, "encoder_colour.pkl"))

joblib.dump(OUTFIT_FEATURES,     os.path.join(save_dir, "outfit_feature_names.pkl"))
joblib.dump(COLOUR_FEATURES,     os.path.join(save_dir, "colour_feature_names.pkl"))

joblib.dump(ALL_OUTFITS,         os.path.join(save_dir, "outfit_catalogue.pkl"))
joblib.dump(ALL_COLOURS,         os.path.join(save_dir, "colour_catalogue.pkl"))

print(f"\nSaved → {save_dir}/")
print("Files:", sorted(os.listdir(save_dir)))

print("\n" + "=" * 60)
print("FINAL SUMMARY")
print("=" * 60)
print(f" Outfit Ranker R2    : {r2_out:.4f}  {'PASS' if r2_out >= 0.85 else 'FAIL'}")
print(f" Outfit Ranker NDCG@3: {ndcg3:.4f}  {'PASS' if ndcg3 >= 0.95 else 'CHECK'}")
print(f" Colour Ranker R2    : {r2_col:.4f}  {'PASS' if r2_col >= 0.85 else 'FAIL'}")
print(f" Outfit XAI rows     : {len(outfit_xai):,}")
print(f" Colour XAI rows     : {len(colour_xai):,}")
print(f" Total outfits       : {len(ALL_OUTFITS)}")
print(f" Total colour families: {len(ALL_COLOURS)}")
print(f" SHAP explainers saved: YES")