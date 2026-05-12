import os
import json
import hashlib
import requests
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import sys

CACHE_DIR = os.path.join(os.path.dirname(__file__), "../.cache/images")
CACHE_INDEX = os.path.join(CACHE_DIR, "index.json")

def ensure_cache_dir():
    """Create cache directory if it doesn't exist."""
    Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)

def get_cache_index():
    """Load cache index from file."""
    ensure_cache_dir()
    if os.path.exists(CACHE_INDEX):
        try:
            with open(CACHE_INDEX, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache_index(index):
    """Save cache index to file."""
    ensure_cache_dir()
    with open(CACHE_INDEX, "w") as f:
        json.dump(index, f, indent=2)

def prompt_hash(prompt: str) -> str:
    """Generate a hash for a prompt."""
    return hashlib.md5(prompt.lower().strip().encode()).hexdigest()[:12]

def get_cached_image(prompt: str) -> str:
    """Get a cached image URL if it exists, None otherwise."""
    cache_key = prompt_hash(prompt)
    index = get_cache_index()
    
    if cache_key in index:
        entry = index[cache_key]
        image_path = entry.get("image_path")
        if image_path and os.path.exists(image_path):
            # Return backend serving URL
            return f"/api/cache/file/{cache_key}"
    
    return None

def download_and_save_image(image_url: str, cache_key: str) -> str:
    """
    Download image from URL and save to disk.
    Retries if necessary and saves to the cache directory.
    Returns the local file path if successful, None otherwise.
    """
    import time
    
    try:
        # Don't attempt to download placeholder images
        if "placehold.co" in image_url or "placeholder" in image_url.lower():
            print(f"[IMAGE_CACHE] Skipping placeholder: {image_url}", file=sys.stderr, flush=True)
            return None
        
        if image_url.startswith("/generated"):
            image_url = f"http://localhost:8000{image_url}"

        print(f"[IMAGE_CACHE] Downloading: {image_url}", file=sys.stderr, flush=True)
        
        # Retry up to 3 times with delays (in case ComfyUI file is still being written)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Try with SSL verification disabled first
                response = requests.get(image_url, timeout=30, verify=False)
                print(f"[IMAGE_CACHE] Attempt {attempt + 1}: Status {response.status_code}", file=sys.stderr, flush=True)
                
                if response.status_code == 200:
                    break
                elif response.status_code == 404 and attempt < max_retries - 1:
                    print(f"[IMAGE_CACHE] File not found (404), waiting 2s before retry...", file=sys.stderr, flush=True)
                    time.sleep(2)
                    continue
                else:
                    response.raise_for_status()
                    
            except requests.exceptions.SSLError:
                print(f"[IMAGE_CACHE] SSL error, retrying with verification...", file=sys.stderr, flush=True)
                response = requests.get(image_url, timeout=30, verify=True)
        
        if response.status_code != 200:
            print(f"[IMAGE_CACHE] ERROR: HTTP {response.status_code} from {image_url}", file=sys.stderr, flush=True)
            return None
        
        if len(response.content) == 0:
            print(f"[IMAGE_CACHE] ERROR: Empty response from {image_url}", file=sys.stderr, flush=True)
            return None
        
        # Determine file extension from content type or filename
        content_type = response.headers.get("content-type", "image/png")
        if "image/png" in content_type:
            ext = ".png"
        elif  "image/jpeg" in content_type or "image/jpg" in content_type:
            ext = ".jpg"
        elif ".png" in image_url:
            ext = ".png"
        elif ".jpg" in image_url or ".jpeg" in image_url:
            ext = ".jpg"
        else:
            ext = ".png"  # Default to PNG
        
        # Save to disk in cache directory
        ensure_cache_dir()
        image_path = os.path.join(CACHE_DIR, f"{cache_key}{ext}")
        
        try:
            with open(image_path, "wb") as f:
                f.write(response.content)
            
            file_size = os.path.getsize(image_path)
            print(f"[IMAGE_CACHE] ✓ Saved {file_size} bytes to {image_path}", file=sys.stderr, flush=True)
            return image_path
        except IOError as e:
            print(f"[IMAGE_CACHE] ERROR: Failed to write file: {e}", file=sys.stderr, flush=True)
            return None
            
    except requests.exceptions.ConnectionError as e:
        print(f"[IMAGE_CACHE] ERROR: Connection failed: {e}", file=sys.stderr, flush=True)
        return None
    except requests.exceptions.Timeout:
        print(f"[IMAGE_CACHE] ERROR: Timeout downloading {image_url}", file=sys.stderr, flush=True)
        return None
    except requests.exceptions.RequestException as e:
        print(f"[IMAGE_CACHE] ERROR: Request failed: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
        return None
    except Exception as e:
        print(f"[IMAGE_CACHE] ERROR: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return None

def cache_image(prompt: str, image_url: str) -> str:
    """
    Cache an image by downloading it and saving to disk.
    Returns the backend URL to access the cached image.
    If download fails, stores the URL anyway for fallback.
    """
    cache_key = prompt_hash(prompt)
    ensure_cache_dir()
    
    index = get_cache_index()
    
    if cache_key not in index:
        # Try to download and save the image
        print(f"[IMAGE_CACHE] Attempting to cache image for: {prompt[:50]}...", file=sys.stderr, flush=True)
        image_path = download_and_save_image(image_url, cache_key)
        
        if image_path:
            print(f"[IMAGE_CACHE] ✓ Successfully cached image", file=sys.stderr, flush=True)
        else:
            print(f"[IMAGE_CACHE] WARNING: Failed to download image, storing URL as fallback", file=sys.stderr, flush=True)
        
        index[cache_key] = {
            "prompt": prompt,
            "image_url": image_url,  # Keep original URL for reference
            "cached_at": datetime.now().isoformat(),
            "image_path": image_path,  # Local path on disk (may be None if download failed)
        }
        save_cache_index(index)
    
    # Return the backend serving URL
    return f"/api/cache/file/{cache_key}"

def get_or_generate_image(prompt: str, generator_func) -> str:
    """
    Get a cached image for a prompt, or generate a new one.
    
    Args:
        prompt: The image generation prompt
        generator_func: Callable that takes prompt and returns image URL
    
    Returns:
        Image URL (cached or newly generated)
    """
    # Check cache first
    cached = get_cached_image(prompt)
    if cached:
        print(f"Image cache hit for prompt: {prompt[:50]}...")
        return cached
    
    # Generate new image
    print(f"Generating new image for prompt: {prompt[:50]}...")
    image_url = generator_func(prompt)
    
    # Cache it
    return cache_image(prompt, image_url)

def list_cached_images(limit=10):
    """List recently cached images with correct backend URLs."""
    index = get_cache_index()
    items = list(index.items())
    items.sort(key=lambda x: x[1].get("cached_at", ""), reverse=True)
    
    # Convert to list of tuples with updated image_url pointing to backend
    result = []
    for cache_key, entry in items[:limit]:
        updated_entry = entry.copy()
        # Update to point to backend serving endpoint
        updated_entry["image_url"] = f"/api/cache/file/{cache_key}"
        result.append((cache_key, updated_entry))
    
    return result

def get_image_file_path(cache_key: str) -> str:
    """Get the file path for a cached image by cache key."""
    index = get_cache_index()
    if cache_key in index:
        return index[cache_key].get("image_path")
    return None
