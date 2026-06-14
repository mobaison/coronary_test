# setup_mac.py
import os
import subprocess

def setup_mac():
    print("Setting up CoronaryAI on macOS...")
    print("=" * 50)
    
    # Create directories
    directories = [
        'data/uploads',
        'data/results',
        'data/reports',
        'static/css',
        'static/js',
        'static/images',
        'models',
        'utils',
        'templates'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created {directory}/")
    
    # Check and install requirements
    print("\nChecking requirements...")
    try:
        import flask
        print("✓ Flask is installed")
    except:
        print("Installing Flask...")
        subprocess.run(['pip3', 'install', 'flask'])
    
    try:
        import torch
        print("✓ PyTorch is installed")
    except:
        print("Installing PyTorch...")
        subprocess.run(['pip3', 'install', 'torch', 'torchvision'])
    
    try:
        import ultralytics
        print("✓ Ultralytics YOLO is installed")
    except:
        print("Installing Ultralytics...")
        subprocess.run(['pip3', 'install', 'ultralytics'])
    
    print("\n" + "=" * 50)
    print("Setup complete!")
    print("\nTo run the application:")
    print("1. Update model paths in config.py")
    print("2. Run: python3 app.py")
    print("3. Open: http://localhost:5000")
    print("\nFor debugging images, visit: http://localhost:5000/debug_images")

if __name__ == "__main__":
    setup_mac()