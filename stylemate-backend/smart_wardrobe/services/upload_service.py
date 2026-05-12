import os
from smart_wardrobe.models.embedding_model import classify_image
from smart_wardrobe.core.database import wardrobe_collection
from smart_wardrobe.services.openai_service import openai_service

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Standardized categories for CLIP-based auto-tagging
CLOTHING_TYPES = ["t-shirt", "shirt", "jeans", "trousers", "dress", "skirt", "jacket", "coat", "sweater", "hoodie", "shorts", "shoes"]
COLORS = ["black", "white", "red", "blue", "green", "yellow", "orange", "purple", "pink", "brown", "grey", "beige"]
FABRICS = ["cotton", "denim", "leather", "wool", "silk", "polyester", "linen"]

def process_upload(file, user_id, enhance_with_ai=True):
    file_path = f"{UPLOAD_FOLDER}/{file.filename}"

    # Save file
    try:
        with open(file_path, "wb") as f:
            content = file.file.read()
            f.write(content)
    except Exception as e:
        print(f"[Upload Service] Error saving file: {str(e)}")
        return {"error": f"Failed to save file: {str(e)}"}

    # Verify file was saved
    if not os.path.exists(file_path):
        print(f"[Upload Service] File not found after save: {file_path}")
        return {"error": f"File was not saved correctly: {file_path}"}
    
    file_size = os.path.getsize(file_path)
    print(f"[Upload Service] Saved file: {file_path} (size: {file_size} bytes)")

    # 1. Basic local classification (Fast fallback)
    detected_type = classify_image(file_path, CLOTHING_TYPES)
    detected_color = classify_image(file_path, COLORS)
    detected_fabric = classify_image(file_path, FABRICS)
    
    print(f"[Upload Service] Local CLIP Detection - Type: {detected_type}, Color: {detected_color}, Fabric: {detected_fabric}")

    # 2. Enhanced OpenAI Vision Analysis (Deep metadata)
    ai_metadata = {}
    if enhance_with_ai:
        print(f"[Upload Service] Starting OpenAI analysis for: {file_path}")
        ai_metadata = openai_service.analyze_clothing_image(file_path)
        print(f"[Upload Service] OpenAI Response: {ai_metadata}")
        if "error" in ai_metadata:
            print(f"[Upload Service] OpenAI Error: {ai_metadata['error']}")
            ai_metadata = {}

    # Merge data - using field names requested by user
    # Ensure fallback values are not empty
    final_category = (ai_metadata.get("category") or detected_type or "Unknown")
    final_color = (ai_metadata.get("main_color") or detected_color or "Unknown")
    final_fabric = (ai_metadata.get("fabric") or detected_fabric or "Unknown")
    final_item_name = (ai_metadata.get("item_name") or f"{final_color} {final_category}").strip()
    
    cloth_data = {
        "userId": str(user_id),
        "imageUrl": file_path,
        "category": final_category,
        "color": final_color,
        "fabricType": final_fabric,
        "itemName": final_item_name,
        "pattern": ai_metadata.get("pattern", "solid"),
        "style": ai_metadata.get("style", "casual"),
        "suitableOccasions": ai_metadata.get("suitable_occasions", []),
        "weatherSuitability": ai_metadata.get("weather_suitability", []),
        "notes": ai_metadata.get("notes", "")
    }
    
    print(f"[Upload Service] Final cloth_data: {cloth_data}")

    # Save to MongoDB wardrobe collection
    result = wardrobe_collection.insert_one(cloth_data)
    cloth_data["_id"] = str(result.inserted_id)

    return {
        "message": "Upload successful", 
        "data": {
            "id": cloth_data["_id"],
            "itemName": cloth_data["itemName"],
            "category": cloth_data["category"],
            "color": cloth_data["color"],
            "fabricType": cloth_data["fabricType"],
            "imageUrl": file_path,
            "ai_enhanced": enhance_with_ai and bool(ai_metadata)
        }
    }