import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import os

class ImageValidator:
    def __init__(self, model_path=None, confidence_threshold=0.65):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.confidence_threshold = confidence_threshold  # Configurable threshold
        self.model = self.load_model(model_path)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        self.CLASS_NAMES = ['Angiogram', 'Non-Angiogram']
        
    def load_model(self, model_path):
        try:
            if model_path and os.path.exists(model_path):
                # Initialize the same architecture used in training
                model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet18', pretrained=False)
                
                # Recreate the final layer to match 2 classes
                num_ftrs = model.fc.in_features
                model.fc = nn.Linear(num_ftrs, 2)
                
                # Load the trained weights
                print(f"Loading weights from {model_path}...")
                model.load_state_dict(torch.load(model_path, map_location=self.device))
                
                model = model.to(self.device)
                model.eval()
                print("✅ Validator model loaded successfully")
                return model
            else:
                print("⚠️ No validator model found. Using basic validation.")
                return None
        except Exception as e:
            print(f"Error loading validator model: {e}")
            return None
    
    def validate_with_model(self, image_np):
        """Validate using the trained ResNet18 model"""
        try:
            image = Image.fromarray(image_np).convert('RGB')
            tensor_img = self.transform(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(tensor_img)
                probs = torch.nn.functional.softmax(outputs, dim=1)
                conf, preds = torch.max(probs, 1)
                
                pred_index = preds.item()
                confidence = conf.item()
                result = self.CLASS_NAMES[pred_index]
                
                # Debug logging (not shown to user)
                print(f"Debug - Validation result: {result} (confidence: {confidence:.2%})")
                
                # Accept if classified as Angiogram AND confidence > threshold
                if result == 'Angiogram' and confidence > self.confidence_threshold:
                    return True, "Valid coronary angiogram detected"
                elif result == 'Angiogram' and confidence <= self.confidence_threshold:
                    return False, "Image quality is insufficient for analysis"
                else:
                    return False, "Image is not a coronary angiogram"
                    
        except Exception as e:
            print(f"Error in model validation: {e}")
            return False, "Error processing image"
    
    def basic_validation(self, image_np):
        """Basic validation based on image properties"""
        if len(image_np.shape) != 3:
            return False, "Invalid image format"
            
        h, w, c = image_np.shape
        
        # Check if image is grayscale-like (angiograms are usually grayscale)
        if c == 3:
            # Check if it's approximately grayscale
            r, g, b = image_np[:,:,0], image_np[:,:,1], image_np[:,:,2]
            if np.mean(np.abs(r - g)) > 30 or np.mean(np.abs(r - b)) > 30:
                return False, "Image appears to be color, not a standard angiogram"
        
        # Check image size
        if h < 100 or w < 100:
            return False, "Image too small for analysis"
        
        # Check if image appears to be medical/angiogram-like
        mean_intensity = np.mean(image_np)
        if mean_intensity < 30 or mean_intensity > 220:
            return False, "Image brightness outside expected range for angiograms"
        
        return True, "Image appears to be a valid angiogram"
    
    def validate(self, image_np):
        """
        Validate if image is a coronary angiogram
        
        Returns:
            tuple: (is_valid, message) - message does NOT include confidence
        """
        try:
            if self.model is not None:
                # Use the trained model
                return self.validate_with_model(image_np)
            else:
                # Use basic validation for demo
                return self.basic_validation(image_np)
                
        except Exception as e:
            print(f"Error validating image: {e}")
            return False, "Error validating image"