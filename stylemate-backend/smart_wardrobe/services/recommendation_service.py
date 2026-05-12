from smart_wardrobe.services.stylist_service import AIStylistEngine

def recommend_outfit(user_id, prompt):
    """
    Main AI Stylist endpoint for generating outfit recommendations.
    """
    try:
        outfits = AIStylistEngine.generate_outfits(
            user_id=user_id,
            prompt=prompt,
            num_outfits=3
        )

        if not outfits:
            return {"message": "No suitable outfits found in your wardrobe for this request."}

        return {"outfits": outfits}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}