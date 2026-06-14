import torch
from models.image_validator import ImageValidator
from models.stenosis_detector import StenosisDetector
from models.segment_classifier import SegmentClassifier
from models.artery_classifier import ArteryClassifier
from PIL import Image
import numpy as np

def test_image_validator():
    print("Testing Image Validator...")
    validator = ImageValidator('/Users/mobaisonoinam/Documents/scikit/classify_stenosis/angiogram_resnet18_weights.pth')
    
    # Test with a sample image
    test_image = np.random.rand(512, 512, 3) * 255
    test_image = test_image.astype(np.uint8)
    
    is_valid, message = validator.validate(test_image)
    print(f"Validation result: {is_valid} - {message}")

def test_stenosis_detector():
    print("\nTesting Stenosis Detector...")
    detector = StenosisDetector('arcade1/bestyolo.pt', confidence_threshold=0.5)
    
    # Test with a sample image
    test_image = np.random.rand(512, 512, 3) * 255
    test_image = test_image.astype(np.uint8)
    
    detections = detector.detect(test_image)
    print(f"Found {len(detections)} stenosis detections")

def main():
    print("Testing ML Models...")
    print("=" * 50)
    
    # Test each model
    test_image_validator()
    test_stenosis_detector()
    
    print("\n" + "=" * 50)
    print("Testing complete!")

if __name__ == "__main__":
    main()