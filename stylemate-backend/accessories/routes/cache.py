from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generation.image_cache import list_cached_images, get_image_file_path, get_cache_index, CACHE_DIR, ensure_cache_dir, save_cache_index

router = APIRouter()

@router.get("/cache/images")
def get_cached_images(limit: int = 10):
    """
    Get list of recently cached generated images with their prompts.
    """
    try:
        images = list_cached_images(limit=limit)
        print(f"[CACHE] Retrieved {len(images)} cached images")
        return {
            "cached_images": [
                {
                    "id": cache_key,
                    "prompt": entry.get("prompt", ""),
                    "image_url": entry.get("image_url", ""),
                    "cached_at": entry.get("cached_at", ""),
                }
                for cache_key, entry in images
            ]
        }
    except Exception as e:
        print(f"[ERROR] in get_cached_images: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache/file/{cache_key}")
def get_cached_file(cache_key: str):
    """
    Serve a cached image file by its cache key.
    If file is missing, returns placeholder message with cache key.
    """
    try:
        file_path = get_image_file_path(cache_key)
        
        # If we have a local file that exists, serve it
        if file_path and os.path.exists(file_path):
            _, ext = os.path.splitext(file_path)
            media_type = "image/png" if ext.lower() == ".png" else "image/jpeg"
            
            print(f"[CACHE] ✓ Serving local file: {file_path}", file=sys.stderr, flush=True)
            return FileResponse(
                file_path,
                media_type=media_type,
                headers={"Cache-Control": "public, max-age=31536000"}
            )
        
        # File doesn't exist - this shouldn't happen in normal flow
        print(f"[CACHE] ERROR: File missing for cache_key: {cache_key}", file=sys.stderr, flush=True)
        
        # Try to get the original URL for debugging info
        index = get_cache_index()
        if cache_key in index:
            original_url = index[cache_key].get("image_url", "unknown")
            print(f"[CACHE] Original URL was: {original_url}", file=sys.stderr, flush=True)
        
        raise HTTPException(
            status_code=500, 
            detail=f"Image file not available (cache_key: {cache_key}). ComfyUI may not have saved the file."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[CACHE] ERROR: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
        raise HTTPException(status_code=500, detail=str(e))
