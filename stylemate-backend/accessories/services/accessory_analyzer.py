import os
import base64
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

VALID_NECKLINE = [
    "collared",
    "halter",
    "highneck",
    "mock",
    "offshoulder",
    "one-shoulder",
    "round",
    "square",
    "strapless",
    "vneck"
]

VALID_SKIN = [
    "light",
    "mid-light",
    "mid-dark",
    "dark"
]

VALID_COLOR = [
    "red",
    "maroon",
    "orange",
    "brown",
    "blue",
    "teal",
    "purple",
    "gray",
    "black"
]


def analyze_accessory(image_path):
    try:
        with open(image_path, "rb") as f:
            image_base64 = base64.b64encode(
                f.read()
            ).decode("utf-8")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """
Analyze this necklace image.

Return JSON only:

{
 "style":"",
 "suitable_neckline":"",
 "suitable_skin_tone":"",
 "suitable_dress_color":""
}

Allowed neckline:
collared, halter, highneck, mock,
offshoulder, one-shoulder, round,
square, strapless, vneck

Allowed skin tones:
light, mid-light, mid-dark, dark

Allowed dress colors:
red, maroon, orange, brown,
blue, teal, purple, gray, black
"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
        )

        content = response.choices[0].message.content

        cleaned = (
            content.replace("```json", "")
            .replace("```", "")
            .strip()
        )

        result = json.loads(cleaned)

        if result["suitable_neckline"] not in VALID_NECKLINE:
            result["suitable_neckline"] = "round"

        if result["suitable_skin_tone"] not in VALID_SKIN:
            result["suitable_skin_tone"] = "mid-light"

        if result["suitable_dress_color"] not in VALID_COLOR:
            result["suitable_dress_color"] = "black"

        return result

    except Exception as e:
        print(f"Accessory analyzer error: {e}")
        return None