import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

device = "cpu"

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")


# TEXT EMBEDDING
def get_text_embedding(text):
    try:
        # Ensure text is a list of strings
        if isinstance(text, str):
            text = [text]

        inputs = processor(
            text=text,
            return_tensors="pt",
            truncation=True,
            max_length=77  # FIX CLIP LIMIT
        )

        with torch.no_grad():
            features = model.get_text_features(**inputs)

        embedding = features[0].cpu().numpy()

        return embedding

    except Exception as e:
        print("[ERROR] Text embedding error:", str(e))
        return None


# IMAGE EMBEDDING
def get_image_embedding(image_path):
    try:
        # CLIPProcessor requires a PIL Image, not a file path string
        pil_image = Image.open(image_path).convert("RGB")
        inputs = processor(images=pil_image, return_tensors="pt")

        with torch.no_grad():
            features = model.get_image_features(**inputs)

        embedding = features[0].cpu().numpy()
        print("[DEBUG] Image embedding shape:", embedding.shape)
        return embedding

    except Exception as e:
        print("[ERROR] Image embedding error:", str(e))
        return None


# ZERO-SHOT CLASSIFICATION
def classify_image(image_path, labels):
    try:
        pil_image = Image.open(image_path).convert("RGB")
        
        # Prepare inputs for both image and candidate labels
        inputs = processor(
            text=labels, 
            images=pil_image, 
            return_tensors="pt", 
            padding=True
        )

        with torch.no_grad():
            outputs = model(**inputs)
        
        # Get image-text similarity scores
        logits_per_image = outputs.logits_per_image # this is the image-text similarity score
        probs = logits_per_image.softmax(dim=1) # we can take the softmax to get probabilities

        best_label_idx = probs.argmax().item()
        return labels[best_label_idx]

    except Exception as e:
        print("[ERROR] Classification error:", str(e))
        return "Unknown"