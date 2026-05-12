from smart_wardrobe.services.stylist_service import AIStylistEngine
from smart_wardrobe.services.weather_service import get_weather_by_city

def plan_trip(user_id, city, days):
    """
    AI Trip Planner: Generates a daily outfit plan and packing list.
    """
    try:
        # 1. Fetch weather forecast for destination
        weather_data = get_weather_by_city(city)
        weather_desc = weather_data.get("weather", [{}])[0].get("description", "mild weather")
        temp = weather_data.get("main", {}).get("temp", 20)
        
        daily_plan = []
        all_packing_items = {}

        # 2. Generate an outfit for each day
        # We use different prompts to ensure variety
        for day in range(1, days + 1):
            prompt = f"travel outfit for day {day} in {city}"
            
            # Generate 1 best outfit for the day
            outfits = AIStylistEngine.generate_outfits(
                user_id=user_id,
                prompt=prompt,
                weather_city=city,
                num_outfits=1
            )
            
            if outfits:
                outfit = outfits[0]
                daily_plan.append({
                    "day": day,
                    "weather": f"{temp}C, {weather_desc}",
                    "outfit": outfit
                })
                
                # Add to packing list (uniquely)
                for item in outfit["items"]:
                    all_packing_items[str(item["id"])] = item

        # 3. Optimize Packing List (Raw items from all outfits)
        packing_list = list(all_packing_items.values())

        return {
            "destination": city,
            "days": days,
            "daily_plan": daily_plan,
            "packing_list": [
                {
                    "type": i.get("type", i.get("category", "other")),
                    "color": i.get("color", ""),
                    "image": i.get("imageUrl", i.get("image", ""))
                } for i in packing_list
            ]
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}