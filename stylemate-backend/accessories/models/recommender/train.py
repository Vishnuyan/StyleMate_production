import torch
import torch.nn as nn
import pandas as pd
import joblib
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# ── Step 1: Load dataset ──────────────────────────────────────────────────────
df = pd.read_csv("dataset/necklace_recommendation_dataset.csv")
print(f"Dataset loaded: {len(df)} rows")
print(df.head())

# ── Step 2: Create and fit label encoders ─────────────────────────────────────
# This creates label_encoders.pkl — must run BEFORE loading it
encoders = {}
for col in ["skin_tone", "neckline", "dress_color", "necklace_style", "metal"]:
    le = LabelEncoder()
    df[col + "_enc"] = le.fit_transform(df[col])
    encoders[col] = le
    print(f"{col}: {list(le.classes_)}")

# Save encoders — needed at inference time
joblib.dump(encoders, "label_encoders.pkl")
print("\nlabel_encoders.pkl saved successfully")

# ── Step 3: Prepare tensors ───────────────────────────────────────────────────
X       = torch.tensor(df[["skin_tone_enc", "neckline_enc", "dress_color_enc"]].values, dtype=torch.float32)
y_style = torch.tensor(df["necklace_style_enc"].values, dtype=torch.long)
y_metal = torch.tensor(df["metal_enc"].values, dtype=torch.long)

print(f"\nX shape      : {X.shape}")
print(f"y_style shape: {y_style.shape}  — {y_style.unique().numel()} unique classes")
print(f"y_metal shape: {y_metal.shape}  — {y_metal.unique().numel()} unique classes")

NUM_STYLES = y_style.unique().numel()   # 9
NUM_METALS = y_metal.unique().numel()   # 10

# ── Step 4: Train/val split ───────────────────────────────────────────────────
indices = list(range(len(X)))
train_idx, val_idx = train_test_split(indices, test_size=0.2, random_state=42)

X_train, X_val         = X[train_idx], X[val_idx]
ys_train, ys_val       = y_style[train_idx], y_style[val_idx]
ym_train, ym_val       = y_metal[train_idx], y_metal[val_idx]

print(f"\nTrain: {len(X_train)} rows  |  Val: {len(X_val)} rows")

# ── Step 5: Define model ──────────────────────────────────────────────────────
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

model     = Recommender(NUM_STYLES, NUM_METALS)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
criterion = nn.CrossEntropyLoss()

# ── Step 6: Training loop ─────────────────────────────────────────────────────
print("\nTraining started...")
best_val_acc = 0.0

for epoch in range(1, 201):
    model.train()
    optimizer.zero_grad()
    s_pred, m_pred = model(X_train)
    loss = criterion(s_pred, ys_train) + criterion(m_pred, ym_train)
    loss.backward()
    optimizer.step()

    # Validation every 20 epochs
    if epoch % 20 == 0:
        model.eval()
        with torch.no_grad():
            vs_pred, vm_pred = model(X_val)
            style_acc = (vs_pred.argmax(1) == ys_val).float().mean().item() * 100
            metal_acc = (vm_pred.argmax(1) == ym_val).float().mean().item() * 100
            val_loss  = (criterion(vs_pred, ys_val) + criterion(vm_pred, ym_val)).item()

        print(f"Epoch {epoch:3d} | Loss: {loss.item():.4f} | Val Loss: {val_loss:.4f} "
              f"| Style acc: {style_acc:.1f}% | Metal acc: {metal_acc:.1f}%")

        # Save best model
        avg_acc = (style_acc + metal_acc) / 2
        if avg_acc > best_val_acc:
            best_val_acc = avg_acc
            torch.save(model.state_dict(), "recommender_model.pth")

# ── Step 7: Final evaluation ──────────────────────────────────────────────────
print("\nFinal evaluation on validation set:")
model.load_state_dict(torch.load("recommender_model.pth"))
model.eval()

with torch.no_grad():
    vs_pred, vm_pred = model(X_val)
    s_pred_labels = vs_pred.argmax(1).numpy()
    m_pred_labels = vm_pred.argmax(1).numpy()

style_names = list(encoders["necklace_style"].classes_)
metal_names = list(encoders["metal"].classes_)

print("\nNecklace Style Classification Report:")
print(classification_report(ys_val.numpy(), s_pred_labels, target_names=style_names))

print("\nMetal Classification Report:")
print(classification_report(ym_val.numpy(), m_pred_labels, target_names=metal_names))

print(f"\nBest model saved to: recommender_model.pth")
print(f"Label encoders saved to: label_encoders.pkl")
print("Training complete.")