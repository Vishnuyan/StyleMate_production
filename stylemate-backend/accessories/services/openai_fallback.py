import os
import base64
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

VALID_SKIN = [
    "light",
    "mid-light",
    "mid-dark",
    "dark"
]

VALID_NECK = [
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


def extract_with_openai(image_path):
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
Analyze this outfit image.

Return ONLY these classes:

Skin tone:
light
mid-light
mid-dark
dark

Neckline:
collared
halter
highneck
mock
offshoulder
one-shoulder
round
square
strapless
vneck

Dress color:
red
maroon
orange
brown
blue
teal
purple
gray
black

Return JSON only:
{
 "skin_tone":"",
 "neckline":"",
 "dress_color":""
}
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
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        result = json.loads(cleaned)

        # validate classes
        if result["skin_tone"] not in VALID_SKIN:
            result["skin_tone"] = None

        if result["neckline"] not in VALID_NECK:
            result["neckline"] = None

        if result["dress_color"] not in VALID_COLOR:
            result["dress_color"] = None

        return result

    except Exception as e:
        print(
            f"OpenAI extraction failed: {e}"
        )
        return None