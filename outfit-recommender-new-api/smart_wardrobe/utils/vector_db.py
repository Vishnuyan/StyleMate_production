import faiss
import numpy as np
from smart_wardrobe.core.database import wardrobe_collection

DIMENSION = 512

# Use IndexFlatIP for cosine similarity (if normalized) or L2 for Euclidean
index = faiss.IndexFlatL2(DIMENSION)
metadata_store = []

def load_vectors_from_db():
    try:
        global metadata_store
        metadata_store = []
        index.reset()

        items = list(wardrobe_collection.find())
        if not items:
            print("[WARN] No items in DB to load into FAISS")
            return

        vectors = []
        for item in items:
            embedding = item.get("embedding")
            if embedding is None:
                continue

            vec = np.array(embedding).astype("float32")
            if vec.shape != (DIMENSION,):
                # Handle cases where embedding might be nested
                vec = vec.flatten()[:DIMENSION]
            
            vectors.append(vec)
            
            # Ensure ObjectId is string and map to 'id' for schema compatibility
            item["id"] = str(item.pop("_id"))
            
            # Map filename to image for schema compatibility
            if "filename" in item and "image" not in item:
                item["image"] = item["filename"]
            elif "image" not in item:
                item["image"] = "unknown.jpg"
            
            # Remove embedding from metadata to keep it light
            if "embedding" in item:
                item.pop("embedding")
            
            metadata_store.append(item)

        if vectors:
            vectors = np.array(vectors).astype("float32")
            index.add(vectors)
            print(f"[SUCCESS] FAISS loaded with {index.ntotal} vectors")

    except Exception as e:
        print("[ERROR] FAISS load error:", e)

def add_vector(vector, metadata):
    try:
        if vector is None: return
        
        vec = np.array(vector).astype("float32").flatten()[:DIMENSION]
        vec = vec.reshape(1, -1)

        # Sanitize metadata: map _id to id
        meta = metadata.copy()
        if "_id" in meta:
            meta["id"] = str(meta.pop("_id"))
        elif "id" not in meta:
            meta["id"] = "unknown"
            
        if "embedding" in meta:
            meta.pop("embedding")
 
        index.add(vec)
        metadata_store.append(meta)
        print(f"[SUCCESS] Vector added. Total: {index.ntotal}")
    except Exception as e:
        print("[ERROR] FAISS add error:", e)

def search_similar(query_vector, k=10):
    try:
        if query_vector is None or index.ntotal == 0:
            return []

        vec = np.array(query_vector).astype("float32").flatten()[:DIMENSION]
        vec = vec.reshape(1, -1)

        distances, indices = index.search(vec, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(metadata_store):
                item = metadata_store[idx].copy()
                item["similarity_score"] = float(distances[0][i])
                results.append(item)
        return results
    except Exception as e:
        print("[ERROR] FAISS search error:", e)
        return []

def classify_item_locally(image_path):
    """
    🧠 Zero-Shot Classification using Local CLIP AI.
    Finds the most similar category and color using embeddings.
    """
    from smart_wardrobe.models.embedding_model import get_image_embedding, get_text_embedding
    from sklearn.metrics.pairwise import cosine_similarity
    
    img_emb = get_image_embedding(image_path)
    if img_emb is None:
        return {"category": "Unknown", "color": "Neutral"}

    categories = ["T-shirt", "Shirt", "Pants", "Jeans", "Jacket", "Dress", "Skirt", "Hoodie", "Sweater", "Shoes", "Coat", "Blazer"]
    colors = ["Red", "Blue", "Green", "Black", "White", "Beige", "Brown", "Grey", "Navy", "Pink", "Yellow"]

    # 1. Classify Category
    cat_embs = [get_text_embedding(f"a photo of a {c}") for c in categories]
    cat_sims = cosine_similarity([img_emb], cat_embs)[0]
    best_cat = categories[np.argmax(cat_sims)]

    # 2. Classify Color
    color_embs = [get_text_embedding(f"a {c} color cloth") for c in colors]
    color_sims = cosine_similarity([img_emb], color_embs)[0]
    best_color = colors[np.argmax(color_sims)]

    return {"category": best_cat, "color": best_color}

def get_user_wardrobe(user_id):
    """Retrieve all items for a specific user AND global items from metadata store"""
    user_id_str = str(user_id)
    return [
        item for item in metadata_store 
        if str(item.get("user_id")) == user_id_str or item.get("user_id") is None
    ]