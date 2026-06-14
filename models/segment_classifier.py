import torch
import cv2
import numpy as np
from ultralytics import YOLO
import math
import os

class SegmentClassifier:
    def __init__(self, model_path=None):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = self.load_model(model_path)
        
        # Segment mapping based on SYNTAX score
        self.SEGMENT_MAP = {
            1: 'RCA', 2: 'RCA', 3: 'RCA', 4: 'RCA', 16: 'RCA',
            5: 'LAD', 
            6: 'LAD', 7: 'LAD', 8: 'LAD', 9: 'LAD', 10: 'LAD',
            11: 'LCx', 12: 'LCx', 13: 'LCx', 14: 'LCx', 15: 'LCx'
        }
        
        # Reverse mapping for mock classification
        self.REVERSE_MAP = {
            'RCA': [1, 2, 3, 4, 16],
            'LAD': [5, 6, 7, 8, 9, 10],
            'LCx': [11, 12, 13, 14, 15]
        }
        
    def load_model(self, model_path):
        # Use provided model or fallback
        try:
            if model_path and os.path.exists(model_path):
                model = YOLO(model_path)
            else:
                print("No custom segment model found. Using demo mode...")
                model = None
        except Exception as e:
            print(f"Error loading segment model: {e}")
            model = None
        return model
    
    def calculate_iou(self, bbox1, bbox2):
        """Calculate Intersection over Union for two bounding boxes"""
        x1 = max(bbox1[0], bbox2[0])
        y1 = max(bbox1[1], bbox2[1])
        x2 = min(bbox1[2], bbox2[2])
        y2 = min(bbox1[3], bbox2[3])
        
        # Calculate area of intersection
        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        
        # Calculate area of union
        area1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
        area2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0
    
    def mock_segment_classification(self, stenosis_bbox):
        """Mock segment classification for demo"""
        center_x = (stenosis_bbox[0] + stenosis_bbox[2]) / 2
        
        # Simple mock logic
        if center_x < 300:
            segment_name = 'LAD'
            segment_id = 6  # Mid LAD segment
        elif center_x < 500:
            segment_name = 'LCx'
            segment_id = 12  # Mid LCx segment
        else:
            segment_name = 'RCA'
            segment_id = 2  # Proximal RCA
        
        return {
            'segment_id': segment_id,
            'segment_name': segment_name,
            'method': 'position_based',
            'confidence': 0.75,
            'message': 'Segment estimated based on position (demo mode)'
        }
    
    def classify_segment(self, image_np, stenosis_bbox, search_range=100):
        """
        Classify segment using IoU/nearest approach
        
        Args:
            image_np: Input image
            stenosis_bbox: Bounding box of stenosis [x1, y1, x2, y2]
            search_range: Maximum distance to search for nearest segment
            
        Returns:
            dict: Segment classification result
        """
        try:
            if self.model is not None:
                # Run segmentation model
                results = self.model(image_np)
                
                best_iou = 0
                best_segment = None
                best_segment_id = None
                
                for result in results:
                    if result.masks is not None:
                        # Get segmentation masks
                        masks = result.masks.data.cpu().numpy()
                        boxes = result.boxes.xyxy.cpu().numpy()
                        cls_ids = result.boxes.cls.cpu().numpy().astype(int)
                        
                        for i, (box, cls_id) in enumerate(zip(boxes, cls_ids)):
                            segment_id = cls_id + 1  # Adjust for 0-index
                            
                            # Calculate IoU with stenosis bbox
                            iou = self.calculate_iou(stenosis_bbox, box)
                            
                            if iou > best_iou:
                                best_iou = iou
                                best_segment = self.SEGMENT_MAP.get(segment_id, 'Unknown')
                                best_segment_id = segment_id
                
                if best_iou > 0:
                    return {
                        'segment_id': best_segment_id,
                        'segment_name': best_segment,
                        'method': 'iou',
                        'confidence': best_iou,
                        'message': f'Segment detected with IoU: {best_iou:.2f}'
                    }
            
            # Fallback to mock classification
            return self.mock_segment_classification(stenosis_bbox)
                
        except Exception as e:
            print(f"Error in segment classification: {e}")
            return self.mock_segment_classification(stenosis_bbox)