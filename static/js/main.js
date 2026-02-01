// Laser Engraving File Converter - JavaScript

let uploadedFile = null;
let uploadedFilename = null;
let outputFilename = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadBestPractices();
    setupEventListeners();
});

function setupEventListeners() {
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    const outputType = document.getElementById('outputType');
    
    // File input change
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // Output type change
    outputType.addEventListener('change', handleOutputTypeChange);
}

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

function handleOutputTypeChange() {
    const outputType = document.getElementById('outputType').value;
    const dpiGroup = document.getElementById('dpiGroup');
    const thresholdGroup = document.getElementById('thresholdGroup');
    
    if (outputType === 'png') {
        dpiGroup.style.display = 'block';
    } else {
        dpiGroup.style.display = 'none';
    }
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    // Show loading
    showLoading('Uploading file...');
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.error) {
            showAlert(data.error, 'error');
            hideLoading();
            return;
        }
        
        // Store file info
        uploadedFile = file;
        uploadedFilename = data.filename;
        
        // Update UI
        document.getElementById('fileName').textContent = data.original_filename;
        document.getElementById('fileType').textContent = data.file_type.toUpperCase();
        document.getElementById('fileInfo').style.display = 'block';
        document.getElementById('optionsSection').style.display = 'block';
        
        // Adjust options based on file type
        if (data.file_type === 'raster') {
            document.getElementById('thresholdGroup').style.display = 'none';
        }
        
        hideLoading();
        
        // Scroll to options
        document.getElementById('optionsSection').scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        showAlert('Upload failed: ' + error.message, 'error');
        hideLoading();
    }
}

async function convertFile() {
    if (!uploadedFilename) {
        showAlert('Please upload a file first', 'error');
        return;
    }
    
    const outputType = document.getElementById('outputType').value;
    const dpi = document.getElementById('dpi').value;
    const threshold = document.getElementById('threshold').value;
    const useCase = document.getElementById('useCase').value;
    
    // Show loading
    showLoading('Converting file...');
    document.getElementById('convertBtn').disabled = true;
    
    try {
        const response = await fetch('/api/convert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filename: uploadedFilename,
                output_type: outputType,
                dpi: dpi,
                threshold: threshold,
                use_case: useCase
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            showAlert(data.error, 'error');
            hideLoading();
            document.getElementById('convertBtn').disabled = false;
            return;
        }
        
        // Store output filename
        outputFilename = data.output_filename;
        
        // Update results
        document.getElementById('outputFileName').textContent = data.output_filename;
        document.getElementById('fileSize').textContent = data.file_size_mb + ' MB';
        document.getElementById('materialSuggestion').textContent = data.material_suggestion;
        
        // Show results section
        document.getElementById('resultsSection').style.display = 'block';
        hideLoading();
        document.getElementById('convertBtn').disabled = false;
        
        // Scroll to results
        document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
        
        showAlert('Conversion successful!', 'success');
        
    } catch (error) {
        showAlert('Conversion failed: ' + error.message, 'error');
        hideLoading();
        document.getElementById('convertBtn').disabled = false;
    }
}

function downloadFile() {
    if (!outputFilename) {
        showAlert('No file to download', 'error');
        return;
    }
    
    window.location.href = '/api/download/' + outputFilename;
}

function resetForm() {
    // Reset variables
    uploadedFile = null;
    uploadedFilename = null;
    outputFilename = null;
    
    // Reset form
    document.getElementById('fileInput').value = '';
    document.getElementById('fileInfo').style.display = 'none';
    document.getElementById('optionsSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function loadBestPractices() {
    try {
        const response = await fetch('/api/best-practices');
        const data = await response.json();
        
        const list = document.getElementById('practicesList');
        list.innerHTML = '';
        
        data.practices.forEach(practice => {
            const li = document.createElement('li');
            li.textContent = practice;
            list.appendChild(li);
        });
    } catch (error) {
        console.error('Failed to load best practices:', error);
    }
}

function toggleBestPractices() {
    const list = document.getElementById('bestPracticesList');
    const button = event.target;
    
    if (list.style.display === 'none') {
        list.style.display = 'block';
        button.textContent = 'Hide Best Practices';
    } else {
        list.style.display = 'none';
        button.textContent = 'Show Best Practices';
    }
}

function showLoading(message) {
    const loading = document.getElementById('loadingIndicator');
    if (message) {
        loading.querySelector('p').textContent = message;
    }
    loading.style.display = 'block';
}

function hideLoading() {
    document.getElementById('loadingIndicator').style.display = 'none';
}

function showAlert(message, type) {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    // Insert at top of main section
    const main = document.querySelector('main');
    main.insertBefore(alert, main.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);
    
    // Scroll to alert
    alert.scrollIntoView({ behavior: 'smooth' });
}
