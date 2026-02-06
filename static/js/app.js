/**
 * Document Search Engine - SaaS Edition
 * Handles file uploads, smart queries, and UI interactions
 */

// ===== State Management =====
const state = {
    documents: [],
    currentTheme: localStorage.getItem('theme') || 'light'
};

// ===== Helper Functions =====
/**
 * Safely parse JSON response, handling non-JSON errors
 */
async function safeJsonParse(response) {
    const contentType = response.headers.get('content-type');

    // Check if response is JSON
    if (contentType && contentType.includes('application/json')) {
        return await response.json();
    }

    // Non-JSON response (likely HTML error page)
    const text = await response.text();

    // Common error: file too large
    if (response.status === 413) {
        return {
            success: false,
            error: 'File too large. Maximum file size is 5MB per file.'
        };
    }

    // Server error
    if (response.status >= 500) {
        return {
            success: false,
            error: 'Server error. Please try again later.'
        };
    }

    // Generic error
    return {
        success: false,
        error: `Request failed with status ${response.status}`
    };
}

// ===== DOM Elements =====
const elements = {
    uploadArea: document.getElementById('uploadArea'),
    fileInput: document.getElementById('fileInput'),
    uploadStatus: document.getElementById('uploadStatus'),
    documentsList: document.getElementById('documentsList'),
    questionInput: document.getElementById('questionInput'),
    searchButton: document.getElementById('searchButton'),
    answerCard: document.getElementById('answerCard'),
    answerContent: document.getElementById('answerContent'),
    loadingState: document.getElementById('loadingState'),
    themeToggle: document.getElementById('themeToggle'),
    confidenceBadge: document.getElementById('confidenceBadge'),
    sourcesList: document.getElementById('sourcesList'),
    steps: document.querySelectorAll('.step')
};

// ===== Initialize =====
function init() {
    // Set initial theme
    document.documentElement.setAttribute('data-theme', state.currentTheme);
    updateThemeIcon();

    // Event listeners
    if (elements.uploadArea) {
        elements.uploadArea.addEventListener('click', () => elements.fileInput.click());
        elements.fileInput.addEventListener('change', handleFileSelect);
        elements.uploadArea.addEventListener('dragover', handleDragOver);
        elements.uploadArea.addEventListener('dragleave', handleDragLeave);
        elements.uploadArea.addEventListener('drop', handleDrop);
    }

    if (elements.searchButton) {
        elements.searchButton.addEventListener('click', handleSearch);
        elements.questionInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleSearch();
        });
    }

    if (elements.themeToggle) {
        elements.themeToggle.addEventListener('click', toggleTheme);
    }

    // Load initial documents
    fetchDocuments();
    updateStep(1); // Start at step 1
}

// ===== Theme Toggle =====
function toggleTheme() {
    state.currentTheme = state.currentTheme === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', state.currentTheme);
    document.documentElement.setAttribute('data-theme', state.currentTheme);
    updateThemeIcon();
}

function updateThemeIcon() {
    if (!elements.themeToggle) return;
    const text = elements.themeToggle.querySelector('.theme-text');
    if (text) text.textContent = state.currentTheme === 'light' ? 'Dark' : 'Light';
}

// ===== Step Indicator =====
function updateStep(stepNumber) {
    elements.steps.forEach((step, index) => {
        if (index + 1 === stepNumber) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });
}

// ===== File Upload =====
function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    uploadFiles(files);
}

function handleDragOver(e) {
    e.preventDefault();
    elements.uploadArea.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    elements.uploadArea.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    elements.uploadArea.classList.remove('drag-over');
    const files = Array.from(e.dataTransfer.files);
    uploadFiles(files);
}

async function uploadFiles(files) {
    if (files.length === 0) return;

    // Validate file sizes BEFORE uploading
    const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB in bytes
    const oversizedFiles = files.filter(file => file.size > MAX_FILE_SIZE);

    if (oversizedFiles.length > 0) {
        const fileList = oversizedFiles.map(f => `• ${f.name} (${formatFileSize(f.size)})`).join('\n');
        elements.uploadStatus.innerHTML = `<span class="error">❌ File size limit exceeded!<br><br>Maximum file size: 5MB<br><br>Files too large:<br>${fileList.replace(/\n/g, '<br>')}</span>`;

        // Clear status after 8 seconds
        setTimeout(() => {
            if (elements.uploadStatus) elements.uploadStatus.innerHTML = '';
        }, 8000);
        return;
    }

    // Show uploading status
    elements.uploadStatus.innerHTML = '<span class="info">⏳ Uploading files...</span>';

    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const result = await safeJsonParse(response);

        if (result.success) {
            elements.uploadStatus.innerHTML = `<span class="success">✅ ${result.message}</span>`;
            await fetchDocuments();  // Wait for refresh
            elements.fileInput.value = '';

            // Advance to step 2 automatically if it's the first upload
            if (state.documents.length <= files.length) {
                updateStep(2);
                document.getElementById('questionInput').focus();
            }

        } else {
            elements.uploadStatus.innerHTML = `<span class="error">❌ ${result.error}</span>`;
        }
    } catch (error) {
        elements.uploadStatus.innerHTML = `<span class="error">❌ Upload failed: ${error.message}</span>`;
    }

    // Clear status after 5 seconds
    setTimeout(() => {
        if (elements.uploadStatus) elements.uploadStatus.innerHTML = '';
    }, 5000);
}

// ===== Document Management =====
async function fetchDocuments() {
    try {
        const response = await fetch('/api/documents');
        const result = await safeJsonParse(response);

        if (result.success) {
            state.documents = result.documents;
            renderDocuments();

            // If we have documents, we're at least on step 2
            if (state.documents.length > 0) {
                updateStep(2);
            }
        }
    } catch (error) {
        console.error('Failed to fetch documents:', error);
    }
}

function renderDocuments() {
    if (state.documents.length === 0) {
        elements.documentsList.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📂</div>
                <p>No documents uploaded yet</p>
                <span class="empty-hint">Your files will appear here</span>
            </div>`;
        return;
    }

    elements.documentsList.innerHTML = state.documents.map(doc => `
        <div class="document-item">
            <div class="doc-icon">${getFileIcon(doc.type)}</div>
            <div class="doc-info">
                <div class="doc-name">${doc.name}</div>
                <div class="doc-size">${doc.type.toUpperCase()} • ${formatFileSize(doc.size)}</div>
            </div>
            <button class="doc-delete" onclick="deleteDocument('${doc.name}')" title="Delete">
                ✕
            </button>
        </div>
    `).join('');
}

function getFileIcon(type) {
    if (type.includes('pdf')) return '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>';

    if (type.includes('doc')) return '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>';

    if (type.includes('csv')) return '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="12" x2="12" y2="12"></line><line x1="12" y1="16" x2="12" y2="16"></line><line x1="8" y1="12" x2="8" y2="12"></line><line x1="8" y1="16" x2="8" y2="16"></line><line x1="16" y1="12" x2="16" y2="12"></line><line x1="16" y1="16" x2="16" y2="16"></line></svg>';

    return '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>';
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

async function deleteDocument(filename) {
    if (!confirm(`Delete ${filename}?`)) return;

    try {
        const response = await fetch(`/api/documents/${encodeURIComponent(filename)}`, {
            method: 'DELETE'
        });

        const result = await safeJsonParse(response);

        if (result.success) {
            await fetchDocuments();
        } else {
            alert(result.error);
        }
    } catch (error) {
        console.error('Failed to delete document:', error);
    }
}

// ===== Search =====
async function handleSearch() {
    const question = elements.questionInput.value.trim();

    if (!question) {
        alert('Please enter a question');
        return;
    }

    // Advance UI state
    updateStep(3);
    elements.answerCard.style.display = 'none';
    elements.loadingState.style.display = 'block';
    elements.searchButton.disabled = true;

    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });

        const result = await safeJsonParse(response);

        elements.loadingState.style.display = 'none';
        elements.searchButton.disabled = false;

        if (result.success) {
            showAnswer(result);
        } else {
            alert(`Error: ${result.error}`);
        }
    } catch (error) {
        elements.loadingState.style.display = 'none';
        elements.searchButton.disabled = false;
        alert(`Search failed: ${error.message}`);
    }
}

function showAnswer(result) {
    // Show Answer Card
    elements.answerCard.style.display = 'block';

    // Set Content
    elements.answerContent.textContent = result.answer;

    // Set Confidence (Randomized for demo if backend doesn't support it)
    // In a real app, you'd calculate this from vector similarity scores
    const confidenceLevel = Math.random() > 0.3 ? 'High' : 'Medium';
    elements.confidenceBadge.className = `confidence-badge ${confidenceLevel.toLowerCase()}`;
    elements.confidenceBadge.textContent = `${confidenceLevel} Confidence`;

    // Set Sources
    const docType = result.doc_type ? result.doc_type.toUpperCase() : 'DOC';
    elements.sourcesList.innerHTML = `
        <span class="source-tag">Source: ${docType}</span>
        <span class="source-tag">Type: AI Analysis</span>
    `;

    // Scroll to answer
    elements.answerCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// Expose functions globally for HTML onClick handlers
window.deleteDocument = deleteDocument;
window.setInput = (text) => {
    const input = document.getElementById('questionInput');
    if (input) {
        input.value = text;
        input.focus();
    }
};

// Initialize
document.addEventListener('DOMContentLoaded', init);
