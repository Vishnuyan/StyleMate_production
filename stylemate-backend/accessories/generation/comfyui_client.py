# import os
# import requests
# import json
# import uuid
# import time
# from dotenv import load_dotenv
# load_dotenv()

# COMFYUI_URL = os.getenv("COMFYUI_URL", "http://127.0.0.1:8188")
# PLACEHOLDER_IMAGE = "https://placehold.co/1024x1024/e8f0f8/4a7ba7?text=Generated+Necklace"

# def is_comfyui_available() -> bool:
#     """Check if ComfyUI server is running and accessible."""
#     try:
#         response = requests.get(f"{COMFYUI_URL}/system_stats", timeout=3)
#         return response.status_code == 200
#     except:
#         return False

# def wait_for_image(prompt_id: str, max_wait: int = 60, poll_interval: float = 2.0) -> dict or None:
#     """
#     Poll ComfyUI history endpoint to wait for image generation.
    
#     Args:
#         prompt_id: The prompt ID returned by ComfyUI
#         max_wait: Maximum seconds to wait (default 60)
#         poll_interval: Seconds between polls (default 2)
    
#     Returns:
#         History data if image is ready, None if timeout
#     """
#     start_time = time.time()
#     while time.time() - start_time < max_wait:
#         try:
#             response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}", timeout=5)
#             if response.status_code == 200:
#                 history = response.json()
#                 if prompt_id in history:
#                     print(f"Image generation completed for prompt_id: {prompt_id}")
#                     return history[prompt_id]
#         except Exception as e:
#             print(f"Error polling ComfyUI history: {e}")
        
#         # Wait before polling again
#         time.sleep(poll_interval)
    
#     print(f"Timeout waiting for image generation (waited {max_wait}s)")
#     return None

# def generate_necklace_image(prompt: str) -> str:
#     """
#     Send prompt to ComfyUI and return the generated image URL.
#     Waits for the image to be generated before returning.
    
#     NOTE: ComfyUI must be running locally at COMFYUI_URL.
#     Install ComfyUI separately: https://github.com/comfyanonymous/ComfyUI
    
#     If ComfyUI is unavailable, returns a placeholder image URL for testing/demo.
#     """
#     # Check if ComfyUI is available
#     if not is_comfyui_available():
#         print("WARNING: ComfyUI not available — returning placeholder image")
#         return PLACEHOLDER_IMAGE
#     # Basic ComfyUI API workflow
#     workflow = {
#         "3": {
#             "class_type": "KSampler",
#             "inputs": {
#                 "seed": int(uuid.uuid4()) % 2**31,
#                 "steps": 20,
#                 "cfg": 7.5,
#                 "sampler_name": "euler",
#                 "scheduler": "normal",
#                 "denoise": 1.0,
#                 "model": ["4", 0],
#                 "positive": ["6", 0],
#                 "negative": ["7", 0],
#                 "latent_image": ["5", 0],
#             }
#         },
#         "4": {
#             "class_type": "CheckpointLoaderSimple",
#             "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}
#         },
#         "5": {
#             "class_type": "EmptyLatentImage",
#             "inputs": {"width": 1024, "height": 1024, "batch_size": 1}
#         },
#         "6": {
#             "class_type": "CLIPTextEncode",
#             "inputs": {"text": prompt, "clip": ["4", 1]}
#         },
#         "7": {
#             "class_type": "CLIPTextEncode",
#             "inputs": {
#                 "text": "blurry, low quality, watermark, text, human, person, model",
#                 "clip": ["4", 1]
#             }
#         },
#         "8": {
#             "class_type": "VAEDecode",
#             "inputs": {"samples": ["3", 0], "vae": ["4", 2]}
#         },
#         "9": {
#             "class_type": "SaveImage",
#             "inputs": {"images": ["8", 0], "filename_prefix": "necklace"}
#         }
#     }

#     try:
#         response = requests.post(
#             f"{COMFYUI_URL}/prompt",
#             json={"prompt": workflow},
#             timeout=10  # Shorter timeout for initial request
#         )
#         response.raise_for_status()
#         data = response.json()
#         prompt_id = data.get("prompt_id", "").strip()

#         if not prompt_id:
#             print("WARNING: ComfyUI returned invalid prompt_id — returning placeholder")
#             return PLACEHOLDER_IMAGE

#         print(f"ComfyUI prompt submitted with ID: {prompt_id}, waiting for generation...")
        
#         # Wait for the image to be generated
#         history = wait_for_image(prompt_id, max_wait=120)
#         if history:
#             try:
#                 # Extract the actual filename from the history
#                 outputs = history.get("outputs", {})
#                 save_image_node = outputs.get("9", {})
#                 images = save_image_node.get("images", [])
                
#                 if images and len(images) > 0:
#                     actual_filename = images[0].get("filename")
#                     subfolder = images[0].get("subfolder", "")
                    
#                     if actual_filename:
#                         # Construct the proper URL with the actual filename
#                         if subfolder:
#                             image_url = f"{COMFYUI_URL}/view?filename={actual_filename}&subfolder={subfolder}"
#                         else:
#                             image_url = f"{COMFYUI_URL}/view?filename={actual_filename}"
#                         print(f"Generated image URL: {image_url}")
#                         return image_url
#             except Exception as e:
#                 print(f"[COMFYUI] Error extracting filename from history: {e}")
            
#             # Fallback: if we couldn't extract the filename, use old format
#             print(f"[COMFYUI] Could not extract actual filename, using fallback format")
#             image_url = f"{COMFYUI_URL}/view?filename=necklace_{prompt_id}.png"
#             print(f"Generated image URL (fallback): {image_url}")
#             return image_url
#         else:
#             print("Image generation timed out after 120 seconds")
#             return PLACEHOLDER_IMAGE

#     except Exception as e:
#         print(f"WARNING: ComfyUI error ({type(e).__name__}: {e}) — returning placeholder")
#         return PLACEHOLDER_IMAGE

import os
import uuid
import base64
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# OpenAI API key
OPENAI_API_KEY2 = os.getenv("OPENAI_API_KEY2")

# Placeholder image if generation fails
PLACEHOLDER_IMAGE = "https://placehold.co/1024x1024/e8f0f8/4a7ba7?text=Generated+Necklace"

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY2)


def generate_necklace_image(prompt: str) -> str:
    """
    Generate necklace image using OpenAI image API
    
    Input:
        prompt -> generated prompt from build_image_prompt()
    
    Output:
        saved image path OR placeholder image
    """

    try:
        print(f"Generating image using OpenAI...")
        print(f"Prompt: {prompt}")

        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )

        if not response.data:
            print("No image returned from OpenAI")
            return PLACEHOLDER_IMAGE

        image_base64 = response.data[0].b64_json

        if not image_base64:
            print("Image data missing")
            return PLACEHOLDER_IMAGE

        # Create folder
        output_folder = "generated_images"
        os.makedirs(output_folder, exist_ok=True)

        # Unique filename
        filename = f"necklace_{uuid.uuid4().hex}.png"
        filepath = os.path.join(output_folder, filename)

        # Save image
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(image_base64))

        print(f"Image saved successfully: {filepath}")

        return filepath

    except Exception as e:
        print(f"OpenAI image generation error: {e}")
        return PLACEHOLDER_IMAGE