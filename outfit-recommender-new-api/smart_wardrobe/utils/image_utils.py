from PIL import Image
import torchvision.transforms as transforms

def load_image(image_path):
    return Image.open(image_path).convert("RGB")

def get_transform():
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(       # CRITICAL FIX
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

def preprocess_image(image_path):
    image = load_image(image_path)
    transform = get_transform()
    return transform(image).unsqueeze(0)