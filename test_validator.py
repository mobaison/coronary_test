# test_validator.py
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import os

def test_validator_model():
    """Test the validator model with different confidence thresholds"""
    
    model_path = '/Users/mobaisonoinam/Documents/scikit/classify_stenosis/angiogram_resnet18_weights.pth'
    
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        return
    
    # Load model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet18', pretrained=False)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, 2)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model = model.to(device)
    model.eval()
    
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    CLASS_NAMES = ['Angiogram', 'Non-Angiogram']
    
    def predict(image_path, threshold=0.65):
        """Make a prediction with given threshold"""
        try:
            image = Image.open(image_path).convert('RGB')
            tensor_img = transform(image).unsqueeze(0).to(device)
            
            with torch.no_grad():
                outputs = model(tensor_img)
                probs = torch.nn.functional.softmax(outputs, dim=1)
                conf, preds = torch.max(probs, 1)
                
                pred_index = preds.item()
                confidence = conf.item()
                result = CLASS_NAMES[pred_index]
                
                # Determine if accepted based on threshold
                accepted = (result == 'Angiogram' and confidence > threshold)
                
                return {
                    'result': result,
                    'confidence': confidence,
                    'accepted': accepted,
                    'threshold': threshold
                }
                
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    # Test with different thresholds
    print("Testing validator model with different confidence thresholds...")
    print("=" * 60)
    
    # You'll need to provide a test image path
    test_image_path = input("Enter path to test image: ").strip()
    
    if not os.path.exists(test_image_path):
        print("Test image not found!")
        return
    
    thresholds = [0.5, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85]
    
    for threshold in thresholds:
        prediction = predict(test_image_path, threshold)
        if prediction:
            print(f"\nThreshold: {threshold:.2f}")
            print(f"Result: {prediction['result']}")
            print(f"Confidence: {prediction['confidence']:.2%}")
            print(f"Accepted: {'YES' if prediction['accepted'] else 'NO'}")
    
    print("\n" + "=" * 60)
    print("Based on these results, choose an appropriate threshold.")
    print("Recommended: Start with 0.65 (65%) and adjust as needed.")

if __name__ == "__main__":
    test_validator_model()