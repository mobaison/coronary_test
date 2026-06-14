import torch
import cv2
import numpy as np
from ultralytics import YOLO
import math

class ArteryClassifier:
    def __init__(self, model_path=None):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = self.load_model(model_path)
        
        # Artery classification mapping
        self.ARTERY_MAP = {
            0: 'LAD',    # Left Anterior Descending
            1: 'LCx',    # Left Circumflex
            2: 'RCA',    # Right Coronary Artery
            3: 'LMA',    # Left Main Artery
            4: 'Other',  # Other/Unknown
        }
        
    def load_model(self, model_path):
        # Use YOLOv8 for now (update to YOLOv11 when available)
        # You can train your own model and use it here
        try:
            if model_path and os.path.exists(model_path):
                model = YOLO(model_path)
            else:
                # Use a pretrained YOLOv8 model as fallback
                # In production, you should train your own artery classifier
                print("Loading fallback artery classifier model...")
                model = YOLO('yolov8n.pt')  # Small model for demo
                # Note: You need to train this model on your artery data
        except Exception as e:
            print(f"Error loading artery model: {e}")
            # Create a mock model for demo purposes
            model = None
        return model
    
    def calculate_iou(self, bbox1, bbox2):
        """Calculate Intersection over Union"""
        x1 = max(bbox1[0], bbox2[0])
        y1 = max(bbox1[1], bbox2[1])
        x2 = min(bbox1[2], bbox2[2])
        y2 = min(bbox1[3], bbox2[3])
        
        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
        area2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0
    
    def mock_classification(self, stenosis_bbox, segment_result=None):
        """Mock artery classification for demo"""
        # In real implementation, this would use actual ML model
        # For demo, we'll simulate based on position and segment
        
        center_x = (stenosis_bbox[0] + stenosis_bbox[2]) / 2
        center_y = (stenosis_bbox[1] + stenosis_bbox[3]) / 2
        
        # Simple mock logic based on position
        if center_x < 300:
            return 'LAD'
        elif center_x < 500:
            return 'LCx'
        elif center_x < 700:
            return 'RCA'
        else:
            return 'LMA'
    
    def classify_artery(self, image_np, stenosis_bbox, segment_result=None, search_range=100):
        """
        Classify artery using IoU/nearest approach
        
        Args:
            image_np: Input image
            stenosis_bbox: Bounding box of stenosis
            segment_result: Optional segment classification result
            search_range: Maximum distance to search
            
        Returns:
            dict: Artery classification result
        """
        try:
            # If we have segment info, use it directly (segment already maps to artery)
            if segment_result and segment_result.get('segment_name') in ['LAD', 'LCx', 'RCA']:
                return {
                    'artery_id': 0,  # Default ID
                    'artery_name': segment_result['segment_name'],
                    'classification_method': 'segment_based',
                    'confidence': 0.85,
                    'message': 'Artery classified based on segment mapping'
                }
            
            # Try to use actual model if available
            if self.model is not None:
                results = self.model(image_np, conf=0.5)
                
                best_iou = 0
                best_artery = 'Unknown'
                best_artery_id = 4
                
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            bbox = box.xyxy[0].cpu().numpy()
                            cls_id = int(box.cls[0].cpu().numpy())
                            
                            # Calculate IoU
                            iou = self.calculate_iou(stenosis_bbox, bbox)
                            
                            if iou > best_iou:
                                best_iou = iou
                                best_artery = self.ARTERY_MAP.get(cls_id, 'Unknown')
                                best_artery_id = cls_id
                
                if best_iou > 0:
                    return {
                        'artery_id': best_artery_id,
                        'artery_name': best_artery,
                        'classification_method': 'iou',
                        'confidence': best_iou,
                        'message': f'Artery detected with IoU: {best_iou:.2f}'
                    }
            
            # Fallback to mock classification for demo
            mock_artery = self.mock_classification(stenosis_bbox, segment_result)
            return {
                'artery_id': list(self.ARTERY_MAP.keys())[list(self.ARTERY_MAP.values()).index(mock_artery)],
                'artery_name': mock_artery,
                'classification_method': 'position_based',
                'confidence': 0.7,
                'message': 'Artery estimated based on position (demo mode)'
            }
            
        except Exception as e:
            print(f"Error in artery classification: {e}")
            return {
                'artery_id': 4,
                'artery_name': 'Unknown',
                'classification_method': 'error',
                'confidence': 0.0,
                'message': str(e)
            }