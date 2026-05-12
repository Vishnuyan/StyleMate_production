import os
import requests
from dotenv import load_dotenv
load_dotenv()

WARDROBE_API_URL = os.getenv("WARDROBE_API_URL", "http://localhost:9000")
WARDROBE_API_KEY = os.getenv("WARDROBE_API_KEY", "")

def get_all_necklaces() -> list:
    """
    Fetch all necklaces from the group member's digital wardrobe API.
    Returns a list of necklace objects.
    
    Replace this URL and logic once you have the wardrobe API from your group member.
    """
    try:
        headers = {}
        if WARDROBE_API_KEY:
            headers["Authorization"] = f"Bearer {WARDROBE_API_KEY}"

        response = requests.get(
            f"{WARDROBE_API_URL}/api/necklaces",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    except Exception as e:
        # Return mock data on any error (connection, invalid URL, etc.)
        print(f"WARNING: Wardrobe API error ({type(e).__name__}: {e}) — returning mock data")
        return [
            {"id": "n001", "style": "pendant",  "metal": "gold",   "color": "yellow", "image_url": ""},
            {"id": "n002", "style": "choker",   "metal": "silver", "color": "white",  "image_url": ""},
            {"id": "n003", "style": "lariat",   "metal": "gold",   "color": "yellow", "image_url": ""},
            {"id": "n004", "style": "statement","metal": "bronze", "color": "brown",  "image_url": ""},
            {"id": "n005", "style": "bar",      "metal": "silver", "color": "white",  "image_url": ""},
        ]