from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY", "").strip()
client = OpenAI(api_key=api_key) if api_key and not api_key.startswith("sk-...") else None

def build_sdxl_prompt(recommendation: dict) -> str:
    """
    Build an SDXL prompt using OpenAI GPT-4o.
    If API key is not configured, returns a mock prompt for testing.
    """
    style  = recommendation.get("necklace_style", "pendant")
    metal  = recommendation.get("metal", "gold")
    skin   = recommendation.get("skin_tone", "light")
    color  = recommendation.get("dress_color", "blue")

    # If OpenAI API is not configured, return a mock prompt
    if client is None:
        print("WARNING: OpenAI API key not configured — returning mock prompt")
        return (
            f"Professional product photography of a {metal} {style} necklace, "
            # f"on a {color} dress, {skin} skin tone wearer, "
            f"clean white background, soft studio lighting, ultra detailed, 4k, "
            f"jewelry photography, no model, necklace only"
        )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional jewelry product photographer. "
                        "Write detailed, vivid image generation prompts for SDXL. "
                        "Output only the prompt text — no explanation, no quotes, nothing else."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Write an SDXL image generation prompt for: "
                        f"a {metal} {style} necklace. "
                        f"The wearer has {skin} skin tone and is wearing a {color} dress. "
                        f"Style: product photography, clean white background, "
                        f"soft studio lighting, ultra detailed, 4k resolution, "
                        f"jewelry photography, no model, necklace only."
                    )
                }
            ],
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"ERROR: OpenAI API call failed: {e}")
        # Fallback mock prompt
        return (
            f"Professional product photography of a {metal} {style} necklace, "
            # f"on a {color} dress, {skin} skin tone wearer, "
            f"clean white background, soft studio lighting, ultra detailed, 4k, "
            f"jewelry photography, no model, necklace only"
        )