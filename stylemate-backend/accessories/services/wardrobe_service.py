import os
import requests
from dotenv import load_dotenv

load_dotenv()

WARDROBE_API_URL = os.getenv(
    "WARDROBE_API_URL",
    "http://localhost:9000"
)

WARDROBE_API_KEY = os.getenv(
    "WARDROBE_API_KEY",
    ""
)


def get_user_necklaces(user_id: str):
    try:
        headers = {}

        if WARDROBE_API_KEY:
            headers["Authorization"] = (
                f"Bearer {WARDROBE_API_KEY}"
            )

        response = requests.get(
            f"{WARDROBE_API_URL}/api/users/{user_id}/necklaces",
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        return response.json()

    except Exception as e:
        print(
            f"Wardrobe API error: {e}"
        )

        # temporary mock data
        return [
            {
                "id": "n001",
                "style": "pendant",
                "metal": "gold",
                "color": "yellow",
                "image_url": ""
            },
            {
                "id": "n002",
                "style": "choker",
                "metal": "silver",
                "color": "white",
                "image_url": ""
            }
        ]