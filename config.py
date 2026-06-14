import os

# Get the absolute path to the project directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-for-demo'
    
    # File upload configuration - using absolute paths
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'data/uploads')
    RESULT_FOLDER = os.path.join(BASE_DIR, 'data/results')
    REPORT_FOLDER = os.path.join(BASE_DIR, 'data/reports')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'tif'}
    
    VALIDATOR_MODEL_PATH = 'project_final16/models/angiogram_resnet18_weights.pth'
    STENOSIS_MODEL_PATH = 'project_final16/models/stenosis.pt'
    SEGMENT_MODEL_PATH = 'project_final16/models/segmentation.pt'
    ARTERY_MODEL_PATH = 'project_final16/models/classification.pt'
    

    VALIDATOR_CONFIDENCE_THRESHOLD = 0.65  # 65% confidence threshold (adjust as needed)
    STENOSIS_CONFIDENCE_THRESHOLD = 0.5    # 50% confidence threshold for stenosis detection
    
    # Debug settings
    DEBUG = True
    