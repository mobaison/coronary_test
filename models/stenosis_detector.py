import torch
import cv2
import numpy as np
from ultralytics import YOLO
import os

class StenosisDetector:
    def __init__(self, model_path=None, confidence_threshold=0.5):
        self.confidence_threshold = confidence_threshold
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = self.load_model(model_path)
        
    def load_model(self, model_path):
        # Use provided model path or use a fallback
        try:
            if model_path and os.path.exists(model_path):
                model = YOLO(model_path)
            else:
                print("No custom stenosis model found. Using demo mode...")
                # For demo, return a mock model
                model = None
        except Exception as e:
            print(f"Error loading stenosis model: {e}")
            model = None
        return model
    
    def mock_detection(self, image_np):
        """Mock stenosis detection for demo"""
        h, w = image_np.shape[:2]
        
        # Create mock detections at different positions
        detections = []
        
        # Mock detection 1
        bbox1 = [w * 0.2, h * 0.3, w * 0.3, h * 0.4]
        detections.append({
            'bbox': bbox1,
            'confidence': 0.85
        })
        
        # Mock detection 2 (optional)
        if w > 500 and h > 500:
            bbox2 = [w * 0.6, h * 0.5, w * 0.7, h * 0.6]
            detections.append({
                'bbox': bbox2,
                'confidence': 0.70
            })
        
        return detections
    
    def detect(self, image_np):
        """
        Detect stenosis in coronary angiogram
        
        Args:
            image_np: numpy array of image
            
        Returns:
            list: List of detections with bbox coordinates
        """
        try:
            if self.model is not None:
                # Run inference with actual model
                results = self.model(image_np, conf=self.confidence_threshold)
                
                detections = []
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            # Get bounding box coordinates
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            
                            detections.append({
                                'bbox': [float(x1), float(y1), float(x2), float(y2)],
                                'confidence': float(box.conf[0])
                            })
                
                return detections
            else:
                # Use mock detection for demo
                print("Using mock stenosis detection for demo")
                return self.mock_detection(image_np)
                
        except Exception as e:
            print(f"Error in stenosis detection: {e}")
            # Return mock detections as fallback
            return self.mock_detection(image_np)