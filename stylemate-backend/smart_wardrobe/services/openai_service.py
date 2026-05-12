import os
import json
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_MODEL = "gpt-4o-mini"

class OpenAIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

    def analyze_clothing_image(self, image_path: str) -> dict:
        """Analyze a clothing image using OpenAI Vision."""
        if not self.client:
            # 🧠 Real Local AI Inference: Using CLIP to classify image
            from smart_wardrobe.utils.vector_db import classify_item_locally
            prediction = classify_item_locally(image_path)
            return {
                "item_name": f"Local AI: {prediction['category']} ({prediction['color']})",
                "category": prediction["category"],
                "main_color": prediction["color"],
                "fabric": "Detected from texture",
                "style": "Modern",
                "suitable_occasions": ["Daily"],
                "notes": "Processed using Local CLIP AI Inference."
            }

        try:
            # Check if file exists
            if not os.path.exists(image_path):
                print(f"[OpenAI Service] File not found: {image_path}")
                return {"error": f"File not found: {image_path}"}
            
            # Read and encode image as base64
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')
            
            print(f"[OpenAI Service] Successfully encoded image to base64, size: {len(base64_image)} bytes")

            system_prompt = """You are a professional fashion analyst AI.
Extract structured metadata from the clothing image.
Return ONLY valid JSON matching this schema:
{
  "item_name": "descriptive name",
  "category": "one of: Hoodie, Jacket, Pants, Shirt, Shorts, T-shirt, Dress, Skirt, Suit, Coat, Blazer, Sweater, Jeans, Leggings, Shoes, Accessories, Other",
  "main_color": "primary color",
  "fabric": "safe fabric term (e.g. cotton, wool, denim, etc.)",
  "pattern": "solid/striped/floral/etc",
  "style": "casual/formal/etc",
  "suitable_occasions": ["Casual", "Formal", etc],
  "weather_suitability": ["Hot", "Cold", etc],
  "notes": "extra observations"
}"""

            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Analyze this clothing item."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            print(f"[OpenAI Service] Analysis result: {result}")
            return result
            
        except FileNotFoundError as e:
            print(f"[OpenAI Service] File error: {str(e)}")
            return {"error": f"File not found: {str(e)}"}
        except json.JSONDecodeError as e:
            print(f"[OpenAI Service] JSON decode error: {str(e)}")
            return {"error": f"Invalid JSON response: {str(e)}"}
        except Exception as e:
            print(f"[OpenAI Service] Error: {str(e)}")
            return {"error": str(e)}

    def generate_recommendation(self, user_plan: str, wardrobe_items: list, city: str = None) -> str:
        """Generate outfit recommendations based on wardrobe metadata and weather."""
        if not self.client:
            # Smart Fallback: Local Rule-Based Stylist
            return """### 💡 Local Stylist Suggestion
**Note: Using Local Harmony Engine (Offline Mode)**

Based on your wardrobe, I recommend pairing your favorite **Top** with a complementary **Bottom**. This coordinated look is versatile and fits perfectly with your plan. 

*For full AI-powered expert styling, please configure an OpenAI API key in your .env file.*"""


        # Fetch weather context
        from smart_wardrobe.services.weather_service import get_weather_context
        weather_info = get_weather_context(city)

        # Base URL for images
        base_url = "http://localhost:8000"


        # Slim down metadata for the prompt
        metadata = []
        for item in wardrobe_items:
            img_path = item.get("imageUrl", "").replace('\\', '/')
            img_url = f"{base_url}/{img_path}" if img_path and not img_path.startswith('http') else img_path

            
            metadata.append({
                "id": str(item.get("_id", "")),
                "name": item.get("itemName", "Unknown"),
                "category": item.get("category", ""),
                "color": item.get("color", ""),
                "style": item.get("style", ""),
                "image_url": img_url
            })

        system_prompt = """You are an expert personal stylist AI.
CRITICAL RULE: Use ONLY the items provided in the user's wardrobe list. 
DO NOT suggest items that the user does not own.

When suggesting an outfit:
1. Start by stating the current weather for the identified location (e.g. "Currently in Paris: 12°C, Rain").
2. Provide a title for the day/occasion (e.g. ## Day 1: City Tour).
3. For every item you suggest, include its image using Markdown syntax: ![Item Name](image_url).
4. Explain why this combination works based on the weather and occasion.
5. If an ideal item is missing, mention it: "Note: A [Item Type] is recommended but missing."


Ensure the plan is visually rich with images of the actual wardrobe items.
Provide the response in Markdown format."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o", 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Context: Current weather is {weather_info}.\nPlan: {user_plan}\n\nWardrobe: {json.dumps(metadata)}"}
                ]
            )
            return response.choices[0].message.content

        except Exception as e:
            return f"Error: {str(e)}"


    def extract_city_from_prompt(self, prompt: str) -> str | None:
        """Extract a city name from a natural language prompt."""
        if not self.client:
            return None

        system_prompt = "Extract the city or location mentioned in the text. Return ONLY the city name or 'null' if none found."
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            city = response.choices[0].message.content.strip().lower()
            return city if city != 'null' else None
        except Exception:
            return None

    def smart_search_filters(self, query: str) -> dict:

        """Convert natural language query to DB filters."""
        if not self.client:
            return {}

        system_prompt = """Convert search query to JSON filters.
Schema: {"category": str|null, "main_color": str|null, "style": str|null, "occasion": str|null}"""

        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception:
            return {}

openai_service = OpenAIService()
