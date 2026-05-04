import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from smart_wardrobe.core.database import wardrobe_collection
from collections import Counter

def filter_items_by_context(items, context):
    """
    ⚙️ Filter items based on style context.
    """
    filtered = []
    style = context.get("style", "").lower()

    for item in items:
        # Style filter
        item_style = item.get("style", "").lower()
        if style and style != item_style:
            continue
            
        filtered.append(item)
    return filtered


def color_score(color1, color2):
    """
    💑 Calculate color harmony score.
    """
    color1, color2 = color1.lower(), color2.lower()
    
    # Good combinations: 1.0
    good_combos = [
        ("blue", "white"), ("white", "blue"),
        ("black", "beige"), ("beige", "black"),
        ("white", "black"), ("black", "white"),
        ("navy", "white"), ("white", "navy")
    ]
    if (color1, color2) in good_combos:
        return 1.0
    
    # Same color: 0.8
    if color1 == color2:
        return 0.8
        
    return 0.0

def style_score(style1, style2):
    """
    🧩 Calculate style consistency score.
    """
    return 1.0 if style1.lower() == style2.lower() else 0.0

def embedding_score(emb1, emb2):
    """
    🧠 Calculate cosine similarity between two embeddings.
    """
    if emb1 is None or emb2 is None:
        return 0.5
    e1 = np.array(emb1).reshape(1, -1)
    e2 = np.array(emb2).reshape(1, -1)
    return float(cosine_similarity(e1, e2)[0][0])

def match_couple(userA_items, userB_items):
    """
    💑 Couple Matching Logic (2 users)
    """
    matches = []
    for itemA in userA_items:
        for itemB in userB_items:
            # Avoid matching same categories for variety (Optional but good)
            if itemA.get("type") == itemB.get("type") and itemA.get("type") not in ["shoes"]:
                continue

            c_score = color_score(itemA.get("color", ""), itemB.get("color", ""))
            s_score = style_score(itemA.get("style", ""), itemB.get("style", ""))
            e_score = embedding_score(itemA.get("embedding"), itemB.get("embedding"))

            total_score = c_score + s_score + e_score
            
            matches.append({
                "userA": {
                    "id": str(itemA.get("_id")),
                    "name": itemA.get("itemName", "Item"),
                    "type": itemA.get("category"),
                    "color": itemA.get("color"),
                    "image": itemA.get("imageUrl")
                },
                "userB": {
                    "id": str(itemB.get("_id")),
                    "name": itemB.get("itemName", "Item"),
                    "type": itemB.get("category"),
                    "color": itemB.get("color"),
                    "image": itemB.get("imageUrl")
                },
                "score": round(total_score, 2)
            })
    
    # Sort by score and return top 3
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches[:3]

def match_group(all_user_wardrobes, context):
    """
    👥 Group Matching Logic (3+ users)
    """
    # Step 1: Define Theme
    all_colors = []
    for user_id, items in all_user_wardrobes.items():
        all_colors.extend([i.get("color", "").lower() for i in items if i.get("color")])
    
    if all_colors:
        dominant_color = Counter(all_colors).most_common(1)[0][0]
    else:
        dominant_color = "white"
        
    theme = f"{dominant_color} focused"
    neutral_palette = ["white", "black", "beige", "grey", "navy"]

    # Step 2: Build Group Outfit
    group_outfit = []
    for user_id, items in all_user_wardrobes.items():
        # Filter items by theme color OR neutral palette
        themed_items = [i for i in items if i.get("color", "").lower() == dominant_color or i.get("color", "").lower() in neutral_palette]
        
        if not themed_items:
            themed_items = items # Fallback to any item if no theme match
            
        # Select best item (highest style match or just first for simplicity)
        best_item = themed_items[0] if themed_items else None
        
        if best_item:
            group_outfit.append({
                "user": user_id,
                "item": {
                    "id": str(best_item.get("_id")),
                    "name": best_item.get("itemName", "Item"),
                    "type": best_item.get("category"),
                    "color": best_item.get("color"),
                    "image": best_item.get("imageUrl")
                }
            })
            
    return {
        "theme": theme,
        "group_outfit": group_outfit
    }

def match_multi_user_outfit(user_ids, context):
    """
    🚀 Main entry point for multi-user outfit matching.
    """
    # Fetch wardrobes from MongoDB
    all_user_wardrobes = {}
    for uid in user_ids:
        items = list(wardrobe_collection.find({"userId": uid}))
        if not items:
            continue
        # Pre-filter
        all_user_wardrobes[uid] = filter_items_by_context(items, context)

    if len(all_user_wardrobes) < 2:
        return {"error": "Not enough users with valid wardrobes to match."}

    # Decide logic
    if len(user_ids) == 2:
        u1, u2 = user_ids[0], user_ids[1]
        matches = match_couple(all_user_wardrobes.get(u1, []), all_user_wardrobes.get(u2, []))
        return {
            "type": "couple",
            "matches": matches
        }
    else:
        result = match_group(all_user_wardrobes, context)
        return {
            "type": "group",
            "theme": result["theme"],
            "outfits": [result["group_outfit"]] # Returning list for consistency
        }

def group_outfit_multi_user(user_ids, prompt):
    """
    Backward compatible wrapper for existing /group/multi endpoint.
    """
    context = {
        "type": "group",
        "style": "casual",
        "event": "general",
        "weather": "hot"
    }
    return match_multi_user_outfit(user_ids, context)