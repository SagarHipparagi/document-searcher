"""
Flask API Server for Document Search Engine
Apple-inspired web interface with RAG capabilities
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import glob
from document_processor import DocumentProcessor

app = Flask(__name__, static_folder='static')
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize document processor
processor = None

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve main HTML page"""
    return send_from_directory('static', 'index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads"""
    try:
        if 'files' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        files = request.files.getlist('files')
        uploaded_files = []
        
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                uploaded_files.append(filename)
        
        if not uploaded_files:
            return jsonify({'success': False, 'error': 'No valid files uploaded'}), 400
        
        # Reinitialize processor with new files
        print(f"\n{'='*60}")
        print(f"📤 UPLOAD: Processing {len(uploaded_files)} file(s)")
        print(f"Files: {uploaded_files}")
        print(f"{'='*60}\n")
        
        global processor
        processor = DocumentProcessor()
        success = processor.initialize()
        
        print(f"\n{'='*60}")
        print(f"✅ Upload Complete - Success: {success}")
        if processor:
            print(f"Documents loaded: {processor.get_document_count()}")
            print(f"QA chains: {list(processor.qa_chains.keys())}")
        print(f"{'='*60}\n")
        
        if not success:
            return jsonify({'success': False, 'error': 'Failed to process documents'}), 500
        
        return jsonify({
            'success': True,
            'files': uploaded_files,
            'message': f'Successfully uploaded {len(uploaded_files)} file(s)'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def list_documents():
    """List all uploaded documents"""
    try:
        documents = []
        
        for ext in ALLOWED_EXTENSIONS:
            files = glob.glob(os.path.join(UPLOAD_FOLDER, f'*.{ext}'))
            for filepath in files:
                filename = os.path.basename(filepath)
                size = os.path.getsize(filepath)
                documents.append({
                    'name': filename,
                    'type': ext,
                    'size': size
                })
        
        return jsonify({
            'success': True,
            'documents': documents,
            'count': len(documents)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/documents/<filename>', methods=['DELETE'])
def delete_document(filename):
    """Delete a document"""
    try:
        filename = secure_filename(filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        if os.path.exists(filepath):
            os.remove(filepath)
            
            # Reinitialize processor
            global processor
            processor = DocumentProcessor()
            processor.initialize()
            
            return jsonify({
                'success': True,
                'message': f'Deleted {filename}'
            })
        else:
            return jsonify({'success': False, 'error': 'File not found'}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/query', methods=['POST'])
def query_documents():
    """Process a question and return answer"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'success': False, 'error': 'No question provided'}), 400
        
        print(f"\n{'='*60}")
        print(f"❓ QUERY: {question}")
        print(f"{'='*60}\n")
        
        global processor
        if not processor:
            print("⚠️  Processor not initialized, creating new one...")
            processor = DocumentProcessor()
            success = processor.initialize()
            if not success:
                print("❌ Initialization failed - no documents found")
                return jsonify({
                    'success': False,
                    'error': 'No documents loaded. Please upload documents first.'
                }), 400
        
        print(f"Processor state:")
        print(f"  - Documents: {processor.get_document_count()}")
        print(f"  - QA chains: {list(processor.qa_chains.keys()) if processor.qa_chains else 'None'}")
        print(f"  - Router: {'Exists' if processor.router_chain else 'None'}")
        
        # Query the documents
        result = processor.query(question)
        
        print(f"\nQuery result: {result.get('success')}")
        if result.get('success'):
            print(f"Routed to: {result.get('doc_type')}")
        else:
            print(f"Error: {result.get('error')}")
        print(f"{'='*60}\n")
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    try:
        global processor
        
        if not processor:
            return jsonify({
                'success': True,
                'initialized': False,
                'documents': 0
            })
        
        counts = processor.get_document_count()
        total = sum(counts.values())
        
        return jsonify({
            'success': True,
            'initialized': True,
            'documents': total,
            'by_type': counts
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Document Search Engine - Flask Server")
    print("=" * 60)
    print("📍 Server: http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
