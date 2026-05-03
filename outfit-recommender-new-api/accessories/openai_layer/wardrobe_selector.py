import json
from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY", "").strip()
client = OpenAI(api_key=api_key) if api_key and not api_key.startswith("sk-...") else None

def select_from_wardrobe(features: dict, necklaces: list) -> list:
    """
    Uses GPT-4o to select the best 2-3 necklaces from the user's wardrobe
    based on their outfit features.

    Args:
        features: { skin_tone, neckline, dress_color, necklace_style, metal }
        necklaces: [ { id, style, metal, color, image_url }, ... ]

    Returns:
        [ { id, image_url, reason }, ... ]  — top 2-3 picks
    """
    # If OpenAI API is not configured, return first 2-3 necklaces
    if client is None:
        print("WARNING: OpenAI API key not configured — returning first necklaces")
        necklace_map = {n["id"]: n for n in necklaces}
        return [
            {
                "id": n["id"],
                "image_url": n.get("image_url", ""),
                "reason": f"Matches your {features.get('dress_color', 'outfit')}"
            }
            for n in necklaces[:3]
        ]
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional fashion stylist. "
                        "Select the best 2 to 3 necklaces from the user's wardrobe "
                        "that best complement their outfit. "
                        "Return ONLY a JSON object in this exact format: "
                        '{"selections": [{"id": "...", "reason": "..."}, ...]}'
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"User outfit features:\n{json.dumps(features, indent=2)}\n\n"
                        f"Available necklaces in wardrobe:\n{json.dumps(necklaces, indent=2)}\n\n"
                        "Select the best 2-3 necklaces that match this user's outfit. "
                        "Keep each reason short (1 sentence)."
                    )
                }
            ],
            max_tokens=400,
        )

        result = json.loads(response.choices[0].message.content)
        selections = result.get("selections", [])

        # Attach image_url from original wardrobe list
        necklace_map = {n["id"]: n for n in necklaces}
        for s in selections:
            if s["id"] in necklace_map:
                s["image_url"] = necklace_map[s["id"]].get("image_url", "")

        return selections
    
    except Exception as e:
        print(f"ERROR: OpenAI API call failed: {e}")
        # Fallback: return first 2-3 necklaces
        return [
            {
                "id": n["id"],
                "image_url": n.get("image_url", ""),
                "reason": f"Matches your {features.get('dress_color', 'outfit')}"
            }
            for n in necklaces[:3]
        ]