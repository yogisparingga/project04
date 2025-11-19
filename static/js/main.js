// Global variables
let selectedFile = null;

// DOM Elements
const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const filePreview = document.getElementById('filePreview');
const optionsSection = document.getElementById('optionsSection');
const resultsSection = document.getElementById('resultsSection');
const errorMessage = document.getElementById('errorMessage');

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
});

function setupEventListeners() {
    // File input change
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    uploadBox.addEventListener('dragover', handleDragOver);
    uploadBox.addEventListener('dragleave', handleDragLeave);
    uploadBox.addEventListener('drop', handleDrop);

    // Click to upload
    uploadBox.addEventListener('click', () => fileInput.click());
}

// Drag and drop handlers
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    uploadBox.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    uploadBox.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    uploadBox.classList.remove('drag-over');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

// File selection handler
function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

// Handle selected file
function handleFile(file) {
    selectedFile = file;

    // Validate file
    const validTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png', 'image/tiff', 'image/bmp'];
    if (!validTypes.includes(file.type) && !file.name.match(/\.(pdf|jpg|jpeg|png|tiff|bmp)$/i)) {
        showError('Invalid file type. Please select a PDF or image file.');
        return;
    }

    // Validate file size (16MB max)
    if (file.size > 16 * 1024 * 1024) {
        showError('File too large. Maximum size is 16MB.');
        return;
    }

    // Show preview
    showFilePreview(file);

    // Hide upload box, show options
    uploadBox.style.display = 'none';
    filePreview.style.display = 'block';
    optionsSection.style.display = 'block';
    resultsSection.style.display = 'none';
}

// Show file preview
function showFilePreview(file) {
    const previewImage = document.getElementById('previewImage');
    const fileInfo = document.getElementById('fileInfo');

    // Show image preview or PDF icon
    if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function(e) {
            previewImage.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
        };
        reader.readAsDataURL(file);

        // Show OCR engine option for images
        document.getElementById('ocrEngineGroup').style.display = 'block';
    } else if (file.type === 'application/pdf') {
        previewImage.innerHTML = '<div class="pdf-icon">📄</div>';

        // Hide OCR engine option for PDFs
        document.getElementById('ocrEngineGroup').style.display = 'none';
    }

    // Show file info
    const fileSize = formatFileSize(file.size);
    const fileType = file.type || 'Unknown';

    fileInfo.innerHTML = `
        <div class="file-info-item">
            <strong>File Name:</strong>
            <span>${file.name}</span>
        </div>
        <div class="file-info-item">
            <strong>File Size:</strong>
            <span>${fileSize}</span>
        </div>
        <div class="file-info-item">
            <strong>File Type:</strong>
            <span>${fileType}</span>
        </div>
    `;
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Process file
async function processFile() {
    if (!selectedFile) {
        showError('Please select a file first.');
        return;
    }

    const documentType = document.getElementById('documentType').value;
    const ocrEngine = document.getElementById('ocrEngine').value;

    // Show loading state
    const processBtn = document.querySelector('.btn-success');
    const processButtonText = document.getElementById('processButtonText');
    const processSpinner = document.getElementById('processSpinner');

    processBtn.disabled = true;
    processButtonText.textContent = 'Processing...';
    processSpinner.style.display = 'inline-block';

    // Create form data
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('type', documentType);
    formData.append('ocr_engine', ocrEngine);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Processing failed');
        }

        // Show results
        displayResults(result);

    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'An error occurred while processing the file.');
    } finally {
        // Reset button
        processBtn.disabled = false;
        processButtonText.textContent = 'Process File';
        processSpinner.style.display = 'none';
    }
}

// Display results
function displayResults(result) {
    hideError();

    // Show results section
    resultsSection.style.display = 'block';
    optionsSection.style.display = 'none';

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });

    // Display document info
    displayDocumentInfo(result);

    // Display structured data (KTP/SIM)
    if (result.data.ktp || result.data.sim) {
        displayStructuredData(result);
    } else {
        document.getElementById('structuredData').style.display = 'none';
    }

    // Display extracted text
    displayExtractedText(result);

    // Display download options
    displayDownloadOptions(result);
}

// Display document info
function displayDocumentInfo(result) {
    const content = document.getElementById('documentInfoContent');

    let infoHTML = '<div class="info-grid">';

    infoHTML += `
        <div class="info-item">
            <strong>File Name</strong>
            <span>${result.filename}</span>
        </div>
    `;

    if (result.type === 'pdf') {
        infoHTML += `
            <div class="info-item">
                <strong>Type</strong>
                <span>PDF Document</span>
            </div>
        `;
        if (result.data.char_count) {
            infoHTML += `
                <div class="info-item">
                    <strong>Characters</strong>
                    <span>${result.data.char_count.toLocaleString()}</span>
                </div>
            `;
        }
        if (result.data.tables_count !== undefined) {
            infoHTML += `
                <div class="info-item">
                    <strong>Tables Found</strong>
                    <span>${result.data.tables_count}</span>
                </div>
            `;
        }
        if (result.data.images) {
            infoHTML += `
                <div class="info-item">
                    <strong>Pages</strong>
                    <span>${result.data.images.length}</span>
                </div>
            `;
        }
    } else if (result.type === 'image') {
        infoHTML += `
            <div class="info-item">
                <strong>Type</strong>
                <span>${result.data.document_type || 'Image'}</span>
            </div>
            <div class="info-item">
                <strong>OCR Engine</strong>
                <span>${result.ocr_engine === 'easyocr' ? 'EasyOCR' : 'Tesseract'}</span>
            </div>
        `;
    }

    infoHTML += '</div>';
    content.innerHTML = infoHTML;
}

// Display structured data (KTP/SIM)
function displayStructuredData(result) {
    const structuredDataSection = document.getElementById('structuredData');
    const content = document.getElementById('structuredDataContent');

    structuredDataSection.style.display = 'block';

    let data = result.data.ktp || result.data.sim;
    let dataHTML = '<div class="info-grid">';

    for (const [key, value] of Object.entries(data)) {
        if (value) {
            const label = formatFieldName(key);
            dataHTML += `
                <div class="info-item">
                    <strong>${label}</strong>
                    <span>${value}</span>
                </div>
            `;
        }
    }

    dataHTML += '</div>';
    content.innerHTML = dataHTML;
}

// Format field name
function formatFieldName(fieldName) {
    return fieldName
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

// Display extracted text
function displayExtractedText(result) {
    const textElement = document.getElementById('extractedText');
    const text = result.data.text || '';

    // Limit display to first 2000 characters
    const displayText = text.length > 2000 ? text.substring(0, 2000) + '\n\n... (truncated)' : text;

    textElement.textContent = displayText;
}

// Display download options
function displayDownloadOptions(result) {
    const downloadButtons = document.getElementById('downloadButtons');
    let buttonsHTML = '';

    // Text file
    if (result.data.text_file) {
        buttonsHTML += `
            <a href="/download/${result.data.text_file}" class="download-btn">
                📄 Download Text File
            </a>
        `;
    }

    // JSON file (KTP/SIM)
    if (result.data.json_file) {
        buttonsHTML += `
            <a href="/download/${result.data.json_file}" class="download-btn">
                📊 Download JSON Data
            </a>
        `;
    }

    // Processed image
    if (result.data.processed_image) {
        buttonsHTML += `
            <a href="/download/${result.data.processed_image}" class="download-btn">
                🖼️ Download Processed Image
            </a>
        `;
    }

    downloadButtons.innerHTML = buttonsHTML;
}

// Copy text to clipboard
function copyText() {
    const textElement = document.getElementById('extractedText');
    const text = textElement.textContent;

    navigator.clipboard.writeText(text).then(() => {
        alert('Text copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy text:', err);
        alert('Failed to copy text.');
    });
}

// Reset form
function resetForm() {
    selectedFile = null;
    fileInput.value = '';

    // Reset display
    uploadBox.style.display = 'block';
    filePreview.style.display = 'none';
    optionsSection.style.display = 'none';
    resultsSection.style.display = 'none';

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });

    hideError();
}

// Show error
function showError(message) {
    const errorText = document.getElementById('errorText');
    errorText.textContent = message;
    errorMessage.style.display = 'block';

    // Scroll to error
    errorMessage.scrollIntoView({ behavior: 'smooth' });
}

// Hide error
function hideError() {
    errorMessage.style.display = 'none';
}
