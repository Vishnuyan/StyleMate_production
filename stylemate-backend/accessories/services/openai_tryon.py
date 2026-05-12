import os
import base64
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_tryon(person_image_path: str, necklace_image_path: str) -> bytes:
    prompt = """
Image 1 is a photo of a person.
Image 2 is a necklace product image.

Place the necklace from Image 2 naturally around the neck of the person in Image 1.
Keep the same person, face, pose, clothes, and background unchanged.
Match the necklace size, angle, lighting, and perspective realistically.
Do not add extra jewelry.
Do not change the hairstyle, face, or body shape.
Output one realistic edited image.
"""

    with open(person_image_path, "rb") as person_file, open(necklace_image_path, "rb") as necklace_file:
        result = client.images.edit(
            model="gpt-image-1.5",
            image=[person_file, necklace_file],
            prompt=prompt,
            size="1024x1024"
        )

    image_base64 = result.data[0].b64_json
    return base64.b64decode(image_base64)