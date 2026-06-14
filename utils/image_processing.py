import cv2
import numpy as np
from PIL import Image

def load_image(image_path):
    """Load image from path"""
    try:
        image = Image.open(image_path).convert('RGB')
        return np.array(image)
    except Exception as e:
        raise Exception(f"Error loading image: {str(e)}")

def resize_image(image_np, max_size=1024):
    """Resize image while maintaining aspect ratio"""
    h, w = image_np.shape[:2]
    
    if max(h, w) <= max_size:
        return image_np
    
    if h > w:
        new_h = max_size
        new_w = int(w * (max_size / h))
    else:
        new_w = max_size
        new_h = int(h * (max_size / w))
    
    return cv2.resize(image_np, (new_w, new_h))

def normalize_image(image_np):
    """Normalize image for model input"""
    # Convert to float and normalize to [0, 1]
    image_np = image_np.astype(np.float32) / 255.0
    
    # Normalize with ImageNet stats (common for pre-trained models)
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    image_np = (image_np - mean) / std
    
    return image_np