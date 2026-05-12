import os
import uuid

GENERATED_DIR = "generated"
os.makedirs(GENERATED_DIR, exist_ok=True)

def save_output_image(image_bytes: bytes, extension: str = ".png") -> str:
    filename = f"{uuid.uuid4().hex}{extension}"
    filepath = os.path.join(GENERATED_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(image_bytes)

    return filepath, filename