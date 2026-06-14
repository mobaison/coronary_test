import os
import tempfile
from PIL import Image as PILImage
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm
from reportlab.lib.utils import ImageReader
import numpy as np
import cv2

def create_pdf_with_images(result_data, output_path):
    """Create PDF with embedded images and annotations"""
    
    # Create PDF canvas
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    # Add header
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 1*inch, "CORONARY ANGIOGRAM REPORT")
    
    c.setFont("Helvetica", 12)
    c.drawCentredString(width/2, height - 1.5*inch, 
                       f"Patient: {result_data['patient_name']} | Date: {result_data['timestamp'][:10]}")
    
    # Add page border
    c.setStrokeColorRGB(0.2, 0.4, 0.6)
    c.setLineWidth(2)
    c.rect(0.5*inch, 0.5*inch, width - 1*inch, height - 1*inch)
    
    # Load and add original image
    y_position = height - 2.5*inch
    
    if 'original_filename' in result_data and result_data['original_filename']:
        original_path = os.path.join('data/uploads', result_data['original_filename'])
        if os.path.exists(original_path):
            try:
                # Add title
                c.setFont("Helvetica-Bold", 14)
                c.drawString(1*inch, y_position, "Original Angiogram:")
                y_position -= 0.2*inch
                
                # Load and resize image
                img = PILImage.open(original_path)
                img_width, img_height = img.size
                
                # Calculate scaling to fit page
                max_width = 4*inch
                max_height = 3*inch
                scale = min(max_width/img_width, max_height/img_height)
                new_width = img_width * scale
                new_height = img_height * scale
                
                # Draw image
                c.drawImage(original_path, 1*inch, y_position - new_height, 
                           width=new_width, height=new_height)
                
                # Draw image border
                c.setStrokeColorRGB(0.8, 0.8, 0.8)
                c.setLineWidth(1)
                c.rect(1*inch, y_position - new_height, new_width, new_height)
                
                y_position -= new_height + 0.5*inch
                
            except Exception as e:
                print(f"Error adding original image to PDF: {e}")
                c.setFont("Helvetica", 10)
                c.drawString(1*inch, y_position, "Original image not available")
                y_position -= 0.5*inch
    
    # Add processed image with bounding boxes
    if result_data['stenosis_detected'] and 'processed_filename' in result_data and result_data['processed_filename']:
        processed_path = os.path.join('data/results', result_data['processed_filename'])
        if os.path.exists(processed_path):
            try:
                # Add title
                c.setFont("Helvetica-Bold", 14)
                c.drawString(width/2 + 0.5*inch, height - 2.5*inch, "Analysis Result:")
                
                # Load and resize image
                img = PILImage.open(processed_path)
                img_width, img_height = img.size
                
                # Calculate scaling to fit page
                max_width = 4*inch
                max_height = 3*inch
                scale = min(max_width/img_width, max_height/img_height)
                new_width = img_width * scale
                new_height = img_height * scale
                
                # Draw image
                c.drawImage(processed_path, width/2 + 0.5*inch, height - 2.7*inch - new_height, 
                           width=new_width, height=new_height)
                
                # Draw image border
                c.setStrokeColorRGB(0, 0.8, 0)  # Green border for processed image
                c.setLineWidth(2)
                c.rect(width/2 + 0.5*inch, height - 2.7*inch - new_height, new_width, new_height)
                
                # Add legend
                c.setFont("Helvetica", 9)
                c.setFillColorRGB(0, 0.6, 0)
                c.drawString(width/2 + 0.5*inch, height - 2.9*inch - new_height, 
                            "Green boxes: Detected stenosis")
                
            except Exception as e:
                print(f"Error adding processed image to PDF: {e}")
    
    # Add detection details
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1*inch, y_position, "DETECTION RESULTS")
    y_position -= 0.3*inch
    
    if result_data['stenosis_detected'] and 'detections' in result_data:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1*inch, y_position, f"Total Stenosis Detected: {result_data['detection_count']}")
        y_position -= 0.3*inch
        
        c.setFont("Helvetica", 10)
        for i, detection in enumerate(result_data['detections'], 1):
            # Draw detection box
            c.setStrokeColorRGB(1, 0, 0)  # Red for highlight
            c.setLineWidth(1)
            c.rect(1*inch, y_position - 0.6*inch, width - 2*inch, 0.5*inch)
            
            # Detection info
            info = f"Stenosis #{i}: "
            info += f"Location (X={detection['bbox'][0]:.1f}, Y={detection['bbox'][1]:.1f}) | "
            info += f"Segment: {detection['segment'].get('segment_name', 'Unknown')} | "
            info += f"Artery: {detection['artery'].get('artery_name', 'Unknown')}"
            
            c.drawString(1.1*inch, y_position - 0.4*inch, info)
            y_position -= 0.7*inch
            
            # Add page break if needed
            if y_position < 2*inch:
                c.showPage()
                y_position = height - 1*inch
                c.setFont("Helvetica", 10)
    else:
        c.setFont("Helvetica", 12)
        c.drawString(1*inch, y_position, "✓ No stenosis detected in this angiogram.")
        y_position -= 0.3*inch
    
    # Add clinical recommendations
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, y_position, "CLINICAL RECOMMENDATIONS:")
    y_position -= 0.3*inch
    
    c.setFont("Helvetica", 10)
    recommendations = [
        "• Review findings with a qualified cardiologist",
        "• Consider additional diagnostic tests if indicated",
        "• Correlate with patient clinical presentation",
        "• Follow standard clinical guidelines",
        "• Schedule appropriate follow-up"
    ]
    
    for rec in recommendations:
        c.drawString(1.2*inch, y_position, rec)
        y_position -= 0.2*inch
    
    # Add footer
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawCentredString(width/2, 0.5*inch, 
                       "Generated by CoronaryAI System | For research and demonstration purposes only")
    
    # Save PDF
    c.save()
    return output_path