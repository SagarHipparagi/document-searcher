/**
 * Document Search Engine - Vanilla JavaScript
 * Handles file uploads, queries, and dark/light mode
 */

// ===== State Management =====
const state = {
    documents: [],
    currentTheme: localStorage.getItem('theme') || 'light'
};

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
    answerSource: document.getElementById('answerSource'),
    loadingState: document.getElementById('loadingState'),
    themeToggle: document.getElementById('themeToggle')
};

// ===== Initialize =====
function init() {
    // Set initial theme
    document.documentElement.setAttribute('data-theme', state.currentTheme);
    updateThemeIcon();

    // Event listeners
    elements.uploadArea.addEventListener('click', () => elements.fileInput.click());
    elements.fileInput.addEventListener('change', handleFileSelect);
    elements.uploadArea.addEventListener('dragover', handleDragOver);
    elements.uploadArea.addEventListener('dragleave', handleDragLeave);
    elements.uploadArea.addEventListener('drop', handleDrop);
    elements.searchButton.addEventListener('click', handleSearch);
    elements.questionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });
    elements.themeToggle.addEventListener('click', toggleTheme);

    // Load initial documents
    fetchDocuments();
}

// ===== Theme Toggle =====
function toggleTheme() {
    state.currentTheme = state.currentTheme === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', state.currentTheme);
    document.documentElement.setAttribute('data-theme', state.currentTheme);
    updateThemeIcon();
}

function updateThemeIcon() {
    const text = elements.themeToggle.querySelector('.theme-text');
    text.textContent = state.currentTheme === 'light' ? 'Dark' : 'Light';
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

    // Show uploading status
    elements.uploadStatus.innerHTML = '<span class="info">⏳ Uploading files...</span>';

    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            elements.uploadStatus.innerHTML = `<span class="success">✅ ${result.message}</span>`;
            await fetchDocuments();  // Wait for refresh
            elements.fileInput.value = '';
        } else {
            elements.uploadStatus.innerHTML = `<span class="error">❌ ${result.error}</span>`;
        }
    } catch (error) {
        elements.uploadStatus.innerHTML = `<span class="error">❌ Upload failed: ${error.message}</span>`;
    }

    // Clear status after 5 seconds
    setTimeout(() => {
        elements.uploadStatus.innerHTML = '';
    }, 5000);
}

// ===== Document Management =====
async function fetchDocuments() {
    try {
        const response = await fetch('/api/documents');
        const result = await response.json();

        if (result.success) {
            state.documents = result.documents;
            renderDocuments();
        }
    } catch (error) {
        console.error('Failed to fetch documents:', error);
    }
}

function renderDocuments() {
    if (state.documents.length === 0) {
        elements.documentsList.innerHTML = '<p class="empty-state">No documents uploaded yet</p>';
        return;
    }

    elements.documentsList.innerHTML = state.documents.map(doc => `
        <div class="document-item">
            <div class="document-info">
                <div class="document-name">${doc.name}</div>
                <div class="document-meta">${doc.type.toUpperCase()} • ${formatFileSize(doc.size)}</div>
            </div>
            <button class="document-delete" onclick="deleteDocument('${doc.name}')" title="Delete">
                ×
            </button>
        </div>
    `).join('');
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

        const result = await response.json();

        if (result.success) {
            // Immediately refresh the document list
            await fetchDocuments();

            // Show success message
            elements.uploadStatus.innerHTML = '<span class="success">✅ Document deleted</span>';
            setTimeout(() => { elements.uploadStatus.innerHTML = ''; }, 3000);
        } else {
            // Show error message
            elements.uploadStatus.innerHTML = `<span class="error">❌ ${result.error}</span>`;
            setTimeout(() => { elements.uploadStatus.innerHTML = ''; }, 3000);
        }
    } catch (error) {
        console.error('Failed to delete document:', error);
        elements.uploadStatus.innerHTML = '<span class="error">❌ Delete failed</span>';
        setTimeout(() => { elements.uploadStatus.innerHTML = ''; }, 3000);
    }
}

// ===== Search =====
async function handleSearch() {
    const question = elements.questionInput.value.trim();

    if (!question) {
        alert('Please enter a question');
        return;
    }

    // Hide answer, show loading
    elements.answerCard.style.display = 'none';
    elements.loadingState.style.display = 'block';

    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });

        const result = await response.json();

        // Hide loading
        elements.loadingState.style.display = 'none';

        if (result.success) {
            // Show answer
            elements.answerContent.textContent = result.answer;
            elements.answerSource.textContent = `Source: ${result.doc_type.toUpperCase()} documents`;
            elements.answerCard.style.display = 'block';

            // Scroll to answer
            elements.answerCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        } else {
            alert(`Error: ${result.error}`);
        }
    } catch (error) {
        elements.loadingState.style.display = 'none';
        alert(`Search failed: ${error.message}`);
    }
}

// ===== Initialize on Load =====
document.addEventListener('DOMContentLoaded', init);
