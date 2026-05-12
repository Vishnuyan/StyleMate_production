import cv2
import numpy as np
from rembg import remove
from sklearn.cluster import KMeans
from collections import Counter
from PIL import Image
import io


# -----------------------------------
# REMOVE BACKGROUND
# -----------------------------------
def remove_background(image):
    """
    Accept either a PIL Image or a file path.
    Returns a PIL Image with transparent background.
    """
    try:
        if isinstance(image, str):
            # File path
            with open(image, "rb") as f:
                input_image = f.read()
        elif isinstance(image, Image.Image):
            # PIL Image - convert to bytes
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            input_image = buf.getvalue()
        else:
            raise TypeError("image must be a PIL Image or file path string")

        print("[REMBG] Processing image with rembg...")
        output_image = remove(input_image)
        img = Image.open(io.BytesIO(output_image)).convert("RGBA")
        print("[REMBG] ✓ Background removed")
        return img
    except Exception as e:
        print(f"[REMBG] ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise


# -----------------------------------
# COLOR CLASSIFIER (FINAL FIXED RULES)
# -----------------------------------
def classify_color(r, g, b):
    brightness = (r + g + b) / 3
    hue = np.argmax([r, g, b])   # 0=R, 1=G, 2=B

    # -----------------------------
    # 1. BLACK / WHITE / GRAY
    # -----------------------------
    #if brightness < 55 and max(r, g, b) < 80:
        #return "Black"

    # True Black: dark + neutral
    if brightness < 40 and abs(r - g) < 10 and abs(r - b) < 10 and abs(g - b) < 10:
        return "Black"

    if brightness > 230 and abs(r-g) < 20 and abs(r-b) < 20:
        return "White"

    if abs(r-g) < 15 and abs(r-b) < 15 and 110 < brightness < 230:
        return "Gray"

    # -----------------------------
    # 3. PINK (hot pink / baby pink)
    # -----------------------------
    # Real pink dresses: high red, medium blue, low–medium green
    if r > 200 and b > 120 and g < 150:
        return "Pink"

    # Light pink
    if r > 210 and 160 < g < 200 and b > 150:
        return "Light Pink"

    # 🔥 Dark Pink / Rose (THIS FIX)
    if r > 160 and g < 90 and 60 < b < 120:
        return "Pink"
    
    # -----------------------------
    # 4. RED family
    # -----------------------------
    if r > 170 and g < 90 and b < 110:
        return "Red"

    # dark red
    if r > 120 and g < 60 and b < 80:
        return "Maroon"


# -----------------------------------
    # 2. PURPLE (must come BEFORE blue)
    # ----------------------------------
    
      # Case 1: Blue > all + difference small (common purple)
    if b > r and b > g and (b - r) < 80:
        return "Purple"

    # Case 2: Dark-purple / violet (low G)
    #if (r + b) / 2 > g * 1.4:
     #   return "Purple"

    if abs(r - b) < 40 and g < 100 and b > 90 and r > 90:
        return "Purple"
    
    # -----------------------------
    # 5. GREEN family
    # -----------------------------
    # Fixed: green must dominate
    if g > r and g > b:
        if g < 110:
            return "Dark Green"
        return "Green"

    # -----------------------------
    # 6. BLUE family
    # -----------------------------
    if b > g and b > r:
        if b < 120:
            return "Dark Blue"
        if g > 130:
            return "Teal"
        return "Blue"

    # -----------------------------
    # 7. YELLOW / ORANGE / BROWN
    # -----------------------------
    # Yellow
    if r > 200 and g > 180 and b < 130:
        return "Yellow"

    # Orange
    if r > 200 and 100 < g < 160 and b < 80:
        return "Orange"

    # Brown
    # brown = red > green > blue, medium brightness
    if brightness < 180 and r > g > b and (r - b) > 25:
        return "Brown"


    # -----------------------------
    # Unknown fallback
    # -----------------------------
    return f"Unknown (RGB={r,g,b})"

# -----------------------------------
# MAIN COLOR DETECTION FUNCTION
# -----------------------------------
def detect_dress_color(image, k=3):
    """
    Detect dress color from a PIL Image or file path.
    Returns the dominant color name as a string.
    """
    try:
        # Remove background
        print("[DRESS_COLOR] Removing background...")
        img_rgba = remove_background(image)
        print("[DRESS_COLOR] Background removed, converting to array...")
        img = np.array(img_rgba)

        # Extract alpha mask
        alpha = img[:, :, 3]
        mask = alpha > 0
        rgb_pixels = img[:, :, :3][mask]

        if rgb_pixels.size == 0:
            print("[DRESS_COLOR] No pixels after masking")
            return "Unable to detect"

        # Convert to LAB for clustering
        lab_pixels = cv2.cvtColor(
            rgb_pixels.reshape(-1, 1, 3),
            cv2.COLOR_RGB2LAB
        ).reshape(-1, 3)

        print("[DRESS_COLOR] Running KMeans clustering...")
        # KMeans
        kmeans = KMeans(n_clusters=k, n_init='auto', random_state=42)
        labels = kmeans.fit_predict(lab_pixels)

        dominant_cluster = Counter(labels).most_common(1)[0][0]
        Ld, Ad, Bd = kmeans.cluster_centers_[dominant_cluster]

        # Convert LAB → RGB for final color classification
        rgb_color = cv2.cvtColor(
            np.uint8([[[Ld, Ad, Bd]]]),
            cv2.COLOR_LAB2RGB
        )[0][0]

        r, g, b = map(int, rgb_color)
        result = classify_color(r, g, b)
        print(f"[DRESS_COLOR] ✓ Color detected: {result}")
        return result
    except Exception as e:
        print(f"[DRESS_COLOR] ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return "Error detecting color"
