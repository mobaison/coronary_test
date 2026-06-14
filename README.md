# CoronaryAI - Coronary Angiography Analysis System

CoronaryAI is a web-based artificial intelligence system built with Flask, PyTorch, and Ultralytics YOLO to validate and analyze coronary angiogram images for artery classification, segment detection, and stenosis detection. It automatically generates detailed diagnostic PDF reports with visual overlays of detected stenosis.

## Features

1. **Angiogram Image Validation**: Uses a custom-trained ResNet18 model to verify if the uploaded image is a valid coronary angiogram before running heavy AI checks.
2. **Stenosis Detection**: Detects and localizes coronary artery narrowings (stenosis) with confidence scores using YOLO object detection.
3. **Artery & Segment Classification**: Detects and labels different segments of the coronary artery tree.
4. **Automated Diagnostic Reports**: Generates professional PDF reports including patient info, stenosis severity, processing logs, and visual overlay images.

---

## Directory Structure

```text
├── app.py                  # Main Flask application
├── config.py               # Application and model configurations
├── setup.py                # Setup script to initialize folders
├── verify.py               # Script to verify model loadings
├── test_validator.py       # Test script for image validation
├── requirements.txt        # Python dependency specifications
├── models/                 # Model files (weights are gitignored)
│   ├── artery_classifier.py
│   ├── image_validator.py
│   ├── segment_classifier.py
│   └── stenosis_detector.py
├── utils/                  # Utility functions for reports and processing
│   ├── enhanced_report.py
│   ├── image_processing.py
│   ├── pdf_with_images.py
│   └── report_generator.py
├── static/                 # CSS, JS, and image assets
├── templates/              # HTML template files
└── data/                   # Gitignored user uploads and results directories
    ├── uploads/
    ├── results/
    └── reports/
```

---

## Installation & Setup

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd project_final16
```

### 2. Install Dependencies
It is recommended to use a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Initialize Directory Structure
Run the setup script to create the necessary directories:
```bash
python setup.py
```

### 4. Model Weights Configuration
Due to file size limitations on GitHub, the pre-trained neural network model weights are **not** committed to the repository. Before running the application, you must place the following model files into the `models/` directory:

| Model File | Description | Recommended Path |
| :--- | :--- | :--- |
| `angiogram_resnet18_weights.pth` | Image Validation Weights (ResNet18) | `models/angiogram_resnet18_weights.pth` |
| `stenosis.pt` | Stenosis Detection Weights (YOLO) | `models/stenosis.pt` |
| `segmentation.pt` | Segment Classification Weights (YOLO) | `models/segmentation.pt` |
| `classification.pt` | Artery Tree Classification Weights (YOLO) | `models/classification.pt` |

> [!NOTE]
> Make sure to configure the paths to these weights in [config.py](file:///Users/mobaisonoinam/Documents/arteires_folder/project_final16/config.py) if they differ.

---

## Running the Application

### 1. Verify Model Integrity
To ensure all model weights are correctly placed and can load without errors, run the validation script:
```bash
python verify.py
```

### 2. Launch the Flask Server
Start the development server:
```bash
python app.py
```

Open your browser and navigate to:
[http://localhost:5000](http://localhost:5000)

---

## Contributing and Project Sharing
If you are planning to share this project on GitHub:
- The `.gitignore` is pre-configured to ignore all local uploads, outputs, and model weights (`.pt`, `.pth`), preventing large file transfer blocks.
- Directory placeholders (`.gitkeep` files) ensure the correct folder structure is preserved upon cloning.
