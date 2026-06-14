import os
import uuid
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from PIL import Image
import io
import base64
from utils.report_generator import generate_report
from models.image_validator import ImageValidator
from models.stenosis_detector import StenosisDetector
from models.segment_classifier import SegmentClassifier
from models.artery_classifier import ArteryClassifier
from utils.report_generator import generate_report
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Ensure absolute paths for macOS
app.config['UPLOAD_FOLDER'] = os.path.abspath(app.config['UPLOAD_FOLDER'])
app.config['RESULT_FOLDER'] = os.path.abspath(app.config['RESULT_FOLDER'])
app.config['REPORT_FOLDER'] = os.path.abspath(app.config['REPORT_FOLDER'])

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORT_FOLDER'], exist_ok=True)

print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
print(f"Result folder: {app.config['RESULT_FOLDER']}")

# Initialize models
image_validator = ImageValidator(
    Config.VALIDATOR_MODEL_PATH, 
    confidence_threshold=Config.VALIDATOR_CONFIDENCE_THRESHOLD
)
stenosis_detector = StenosisDetector(
    Config.STENOSIS_MODEL_PATH, 
    confidence_threshold=Config.STENOSIS_CONFIDENCE_THRESHOLD
)
segment_classifier = SegmentClassifier(Config.SEGMENT_MODEL_PATH)
artery_classifier = ArteryClassifier(Config.ARTERY_MODEL_PATH)

# In-memory storage for demo
results_storage = []

@app.route('/')
def index():
    """Home page for image upload"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    """Handle image upload and processing"""
    if 'file' not in request.files:
        return render_template('index.html', error="No file selected")
    
    file = request.files['file']
    patient_name = request.form.get('patient_name', 'Anonymous')
    
    if file.filename == '':
        return render_template('index.html', error="No file selected")
    
    if file and allowed_file(file.filename):
        # Generate unique ID for this session
        session_id = str(uuid.uuid4())[:8]
        original_filename = f"{session_id}_{secure_filename(file.filename)}"
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
        
        print(f"Saving original image to: {original_path}")
        
        # Save original image
        try:
            file.save(original_path)
            print(f"Image saved successfully")
        except Exception as e:
            return render_template('index.html', error=f"Error saving file: {str(e)}")
        
        # Load and validate image
        try:
            image = Image.open(original_path).convert('RGB')
            image_np = np.array(image)
            print(f"Image loaded: {image_np.shape}")
        except Exception as e:
            if os.path.exists(original_path):
                os.remove(original_path)
            return render_template('index.html', error=f"Error loading image: {str(e)}")
        
        # Step 1: Validate if image is coronary angiogram
        is_valid, validation_message = image_validator.validate(image_np)
        
        if not is_valid:
            # Delete the uploaded file if invalid
            if os.path.exists(original_path):
                os.remove(original_path)
            return render_template('index.html', 
                                 error=f"Image rejected: ")
        
        # Step 2: Detect stenosis
        detections = stenosis_detector.detect(image_np)
        print(f"Stenosis detections: {len(detections)}")
        
        if not detections:
            # No stenosis detected
            result_data = {
                'session_id': session_id,
                'patient_name': patient_name,
                'timestamp': datetime.now().isoformat(),
                'original_filename': original_filename,
                'processed_filename': None,
                'stenosis_detected': False,
                'message': 'No coronary stenosis detected in the image.',
                'detection_count': 0
            }
            results_storage.append(result_data)
            return render_template('results.html', **result_data)
        
        # Step 3 & 4: Process each detection
        processed_image = image_np.copy()
        detection_results = []
        
        for i, detection in enumerate(detections):
            bbox = detection['bbox']  # [x1, y1, x2, y2]
            print(f"Detection {i+1}: bbox = {bbox}")
            
            # Draw boundary box (green for stenosis)
            cv2.rectangle(processed_image, 
                         (int(bbox[0]), int(bbox[1])), 
                         (int(bbox[2]), int(bbox[3])), 
                         (0, 255, 0), 2)
            
            # Add "Stenosis" text
            cv2.putText(processed_image, "Stenosis", 
                       (int(bbox[0]), int(bbox[1]) - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Step 3: Classify segment
            segment_result = segment_classifier.classify_segment(image_np, bbox)
            print(f"Segment result: {segment_result}")
            
            # Step 4: Classify artery
            artery_result = artery_classifier.classify_artery(image_np, bbox, segment_result)
            print(f"Artery result: {artery_result}")
            
            detection_results.append({
                'detection_id': i + 1,
                'bbox': bbox,
                'segment': segment_result,
                'artery': artery_result
            })
        
        # Save processed image
        processed_filename = f"result_{original_filename}"
        result_path = os.path.join(app.config['RESULT_FOLDER'], processed_filename)
        print(f"Saving processed image to: {result_path}")
        
        # Convert RGB to BGR for OpenCV saving
        processed_image_bgr = cv2.cvtColor(processed_image, cv2.COLOR_RGB2BGR)
        success = cv2.imwrite(result_path, processed_image_bgr)
        print(f"Processed image saved: {success}")
        
        # Prepare result data
        result_data = {
            'session_id': session_id,
            'patient_name': patient_name,
            'timestamp': datetime.now().isoformat(),
            'original_filename': original_filename,
            'processed_filename': processed_filename,
            'stenosis_detected': True,
            'detections': detection_results,
            'detection_count': len(detections)
        }
        
        results_storage.append(result_data)
        
        # After processing detections, add this:
        # Replace the report generation section with:
        try:
            # Use enhanced PDF report
            from utils.enhanced_report import create_enhanced_pdf_report
            report_path = create_enhanced_pdf_report(result_data, app.config['REPORT_FOLDER'])
            result_data['report_path'] = report_path
            result_data['report_filename'] = os.path.basename(report_path)
            print(f"✅ Enhanced report generated: {report_path}")
        except Exception as e:
            print(f"❌ Error generating enhanced report: {e}")
            # Fallback to basic report
            try:
                report_path = generate_report(result_data, app.config['REPORT_FOLDER'])
                result_data['report_path'] = report_path
                result_data['report_filename'] = os.path.basename(report_path)
                print(f"✅ Basic report generated: {report_path}")
            except Exception as e2:
                print(f"❌ Error generating basic report: {e2}")
                result_data['report_path'] = None
                result_data['report_filename'] = None
        
        return render_template('results.html', **result_data)
    
    return render_template('index.html', error="Invalid file type. Please upload an image file.")


@app.route('/download_report/<session_id>')
def download_report(session_id):
    """Download report for a specific session"""
    for result in results_storage:
        if result['session_id'] == session_id:
            report_path = result.get('report_path')
            if report_path and os.path.exists(report_path):
                # Get clean filename
                filename = result.get('report_filename', 
                                     f"coronary_report_{result['patient_name']}_{session_id}.pdf")
                return send_file(
                    report_path,
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/pdf'
                )
    return "Report not found", 404



@app.route('/debug_images')
def debug_images():
    """Debug page to check uploaded images"""
    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
    processed_files = os.listdir(app.config['RESULT_FOLDER'])
    
    html = f"""
    <h1>Debug Images</h1>
    <h2>Upload Folder: {app.config['UPLOAD_FOLDER']}</h2>
    <p>Files: {uploaded_files}</p>
    <h2>Result Folder: {app.config['RESULT_FOLDER']}</h2>
    <p>Files: {processed_files}</p>
    
    <h3>Uploaded Images:</h3>
    """
    
    for file in uploaded_files:
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            html += f'<p><a href="/uploaded/{file}">{file}</a></p>'
            html += f'<img src="/uploaded/{file}" style="max-width: 200px; margin: 10px;"><br>'
    
    html += "<h3>Processed Images:</h3>"
    for file in processed_files:
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            html += f'<p><a href="/processed/{file}">{file}</a></p>'
            html += f'<img src="/processed/{file}" style="max-width: 200px; margin: 10px;"><br>'
    
    html += '<br><a href="/">Back to Home</a>'
    return html


@app.route('/dashboard')
def dashboard():
    """Dashboard to view all results"""
    return render_template('dashboard.html', results=results_storage)
                        

@app.route('/api/results')
def api_results():
    """API endpoint to get all results"""
    return jsonify(results_storage)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Route to serve uploaded images
@app.route('/uploaded/<filename>')
def serve_uploaded(filename):
    """Serve uploaded files"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        print(f"Error serving uploaded file {filename}: {e}")
        return "Image not found", 404

# Route to serve processed images
@app.route('/processed/<filename>')
def serve_processed(filename):
    """Serve processed files"""
    try:
        return send_from_directory(app.config['RESULT_FOLDER'], filename)
    except Exception as e:
        print(f"Error serving processed file {filename}: {e}")
        return "Image not found", 404

# Keep the old route for compatibility
@app.route('/get_image/<image_type>/<filename>')
def get_image(image_type, filename):
    """Serve images - backward compatibility"""
    if image_type == 'original':
        return serve_uploaded(filename)
    elif image_type == 'processed':
        return serve_processed(filename)
    else:
        return "Invalid image type", 404

@app.route('/static_uploads/<filename>')
def static_uploads(filename):
    """Serve static uploads for debugging"""
    try:
        return send_from_directory('static/uploads', filename)
    except:
        return "Static file not found", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)