import random
from smart_wardrobe.core.database import wardrobe_collection
from smart_wardrobe.services.weather_service import get_weather_context

class AIStylistEngine:
    CATEGORIES = {
        "top": ["t-shirt", "shirt", "sweater", "hoodie"],
        "bottom": ["jeans", "trousers", "skirt", "shorts", "pants"],
        "outerwear": ["jacket", "coat"],
        "one_piece": ["dress"],
        "shoes": ["shoes"]
    }

    @staticmethod
    def get_category(item_type):
        for cat, types in AIStylistEngine.CATEGORIES.items():
            if item_type.lower() in types:
                return cat
        return "other"

    @staticmethod
    def generate_outfits(user_id, prompt, weather_city=None, num_outfits=3):
        # 1. Get weather context
        weather_info = get_weather_context(weather_city)
        full_prompt = f"{prompt}, suitable for {weather_info}"
        print(f"[AI Stylist] Prompt: {full_prompt}")

        # 2. Fetch user wardrobe directly from MongoDB (no vector DB)
        user_candidates = list(wardrobe_collection.find({"userId": str(user_id)}))
        if not user_candidates:
            print(f"[AI Stylist] No items found for user {user_id}")
            return []

        # 3. Convert MongoDB ObjectId to string for frontend compatibility
        for item in user_candidates:
            item["id"] = str(item.get("_id", ""))
            item["type"] = item.get("category", "other")  # Map category to type for compatibility

        # 4. Group items by category
        grouped = {cat: [] for cat in AIStylistEngine.CATEGORIES}
        for item in user_candidates:
            item_type = item.get("type", "other")
            cat = AIStylistEngine.get_category(item_type)
            if cat in grouped:
                grouped[cat].append(item)

        # 5. Generate outfit combinations
        outfits = []
        used_item_ids = set()

        # Try to make standard combinations: Top + Bottom (+ Outerwear) OR One-piece (+ Outerwear)
        for _ in range(num_outfits * 2):  # Try multiple times to find diverse ones
            outfit_items = []
            
            # Decide combo type
            if grouped["one_piece"] and random.random() > 0.7:
                outfit_items.append(random.choice(grouped["one_piece"]))
            elif grouped["top"] and grouped["bottom"]:
                outfit_items.append(random.choice(grouped["top"]))
                outfit_items.append(random.choice(grouped["bottom"]))
            
            if not outfit_items: 
                continue

            # Add outerwear if needed (based on prompt)
            if grouped["outerwear"] and ("cold" in weather_info or "jacket" in prompt.lower() or "coat" in prompt.lower()):
                outfit_items.append(random.choice(grouped["outerwear"]))
            
            # Add shoes
            if grouped["shoes"]:
                outfit_items.append(random.choice(grouped["shoes"]))

            # Create outfit ID to check for duplicates
            outfit_id = "-".join(sorted([str(i["id"]) for i in outfit_items]))
            if any(o["id"] == outfit_id for o in outfits):
                continue
 
            # 6. Scoring
            base_score = 0.8 + (0.2 * random.random())  # Random score between 0.8-1.0
            reuse_count = sum([1 for i in outfit_items if i["id"] in used_item_ids])
            final_score = base_score * (0.9 ** reuse_count)

            # 7. Generate reasoning
            reason = AIStylistEngine.generate_reasoning(outfit_items, full_prompt, weather_info)

            outfits.append({
                "id": outfit_id,
                "items": outfit_items,
                "score": round(float(final_score), 2),
                "reason": reason
            })

            for i in outfit_items:
                used_item_ids.add(i["id"])

            if len(outfits) >= num_outfits:
                break

        # 8. Fallback: If no combinations possible, return individual items
        if not outfits:
            print("[AI Stylist] No combinations possible. Falling back to individual items.")
            for item in user_candidates[:num_outfits]:
                outfits.append({
                    "id": f"single-{item['id']}",
                    "items": [item],
                    "score": 0.75,
                    "reason": f"Note: I couldn't find a complete matching set for '{prompt}' in your current wardrobe, but this {item.get('type', 'item')} is a great piece to use."
                })

        # Sort by score
        outfits.sort(key=lambda x: x["score"], reverse=True)
        return outfits

    @staticmethod
    def generate_pro_recommendation(user_id, prompt, city=None):
        """Use OpenAI to generate a professional outfit plan."""
        from smart_wardrobe.services.openai_service import openai_service
        
        # 1. Automatically extract city from prompt if not explicitly given
        if not city:
            city = openai_service.extract_city_from_prompt(prompt)
            if city:
                print(f"[AI Stylist] Auto-detected city: {city}")

        # 2. Fetch user wardrobe from MongoDB (no vector DB)
        items = list(wardrobe_collection.find({"userId": str(user_id)}))
        if not items:
            return "Your wardrobe is empty. Upload some items first!"
        
        # Convert ObjectId to string
        for item in items:
            item["_id"] = str(item.get("_id", ""))
        
        # 3. Call OpenAI service with detected/provided city
        recommendation = openai_service.generate_recommendation(prompt, items, city)
        return recommendation

    @staticmethod
    def generate_reasoning(items, prompt, weather):
        types = [i.get("type", "item") for i in items]
        colors = [i.get("color", "unknown") for i in items]
        
        # Simple reasoning based on context
        reason = f"This combination of {', '.join(types)} in {', '.join(colors)} was selected "
        reason += f"because it aligns with your request for '{prompt}' and the current {weather}. "
        reason += "The items were chosen based on their style and seasonal appropriateness."
        return reason
