// File upload handling
document.addEventListener('DOMContentLoaded', function() {
    console.log("CoronaryAI System Initialized");
    
    // File upload handling
    const dropArea = document.getElementById('dropArea');
    const fileInput = document.getElementById('imageUpload');
    const fileInfo = document.getElementById('fileInfo');
    const browseButton = document.getElementById('browseButton');
    const uploadForm = document.getElementById('uploadForm');
    
    if (dropArea && fileInput && fileInfo) {
        // Click on drop area
        dropArea.addEventListener('click', function(e) {
            if (e.target !== fileInput && e.target !== browseButton) {
                fileInput.click();
            }
        });
        
        // Browse button
        if (browseButton) {
            browseButton.addEventListener('click', function() {
                fileInput.click();
            });
        }
        
        // File input change
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const file = this.files[0];
                updateFileInfo(file);
                validateFile(file);
            }
        });
        
        // Drag and drop
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });
        
        dropArea.addEventListener('drop', handleDrop, false);
        
        // Form submission
        if (uploadForm) {
            uploadForm.addEventListener('submit', function() {
                const submitBtn = this.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                    
                    // Show loading message
                    const loadingDiv = document.createElement('div');
                    loadingDiv.className = 'alert alert-info mt-3';
                    loadingDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing image... This may take a moment.';
                    this.appendChild(loadingDiv);
                }
            });
        }
    }
    
    // Add click handlers to all image placeholders
    document.querySelectorAll('.image-placeholder').forEach(placeholder => {
        placeholder.addEventListener('click', function() {
            alert('Image failed to load. Please check if the image file exists.');
        });
    });
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight(e) {
    e.preventDefault();
    e.stopPropagation();
    this.classList.add('dragover');
}

function unhighlight(e) {
    e.preventDefault();
    e.stopPropagation();
    this.classList.remove('dragover');
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    const fileInput = document.getElementById('imageUpload');
    
    if (files.length > 0) {
        fileInput.files = files;
        updateFileInfo(files[0]);
        validateFile(files[0]);
    }
}

function updateFileInfo(file) {
    const fileInfo = document.getElementById('fileInfo');
    if (fileInfo) {
        fileInfo.innerHTML = `
            <strong>${file.name}</strong><br>
            <small>Size: ${formatFileSize(file.size)} | Type: ${file.type || 'Unknown'}</small>
        `;
        fileInfo.style.color = '#27ae60';
    }
}

function validateFile(file) {
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/bmp', 'image/tiff'];
    const maxSize = 16 * 1024 * 1024; // 16MB
    
    const fileInfo = document.getElementById('fileInfo');
    
    if (!allowedTypes.includes(file.type.toLowerCase()) && 
        !file.name.toLowerCase().match(/\.(png|jpg|jpeg|bmp|tiff|tif)$/)) {
        fileInfo.innerHTML = `<span style="color: #e74c3c;">
            <i class="fas fa-exclamation-triangle"></i> Invalid file type
        </span>`;
        return false;
    }
    
    if (file.size > maxSize) {
        fileInfo.innerHTML = `<span style="color: #e74c3c;">
            <i class="fas fa-exclamation-triangle"></i> File too large (max 16MB)
        </span>`;
        return false;
    }
    
    return true;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Image error handling
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('img').forEach(img => {
        img.addEventListener('error', function() {
            console.error(`Image failed to load: ${this.src}`);
            this.src = 'https://via.placeholder.com/400x300?text=Image+Not+Found';
            this.alt = 'Image failed to load';
        });
    });
});