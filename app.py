"""
Flask Web Application for Document Search Engine
Provides REST API endpoints and serves the web interface
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from document_processor import DocumentProcessor

# Initialize Flask app
app = Flask(__name__, static_folder='static')
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global document processor instance
doc_processor = None
processor_initialized = False


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def initialize_processor():
    """Initialize the document processor with existing documents"""
    global doc_processor, processor_initialized
    
    if processor_initialized:
        return True
    
    try:
        print("🔄 Initializing document processor...")
        doc_processor = DocumentProcessor()
        success = doc_processor.initialize()
        processor_initialized = success
        return success
    except ValueError as e:
        # Specific handling for missing API key
        if "GROQ_API_KEY" in str(e):
            print("❌ DEPLOYMENT ERROR: GROQ_API_KEY environment variable not found!")
            print("📝 Fix: Add GROQ_API_KEY to your deployment platform's environment variables")
            print("   - Render: Dashboard → Environment → Add Environment Variable")
            print("   - Heroku: heroku config:set GROQ_API_KEY=your_key_here")
        raise
    except Exception as e:
        print(f"❌ Error initializing processor: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


@app.route('/')
def index():
    """Serve the main web interface"""
    return send_from_directory('static', 'index.html')


@app.route('/api/status', methods=['GET'])
def status():
    """Get system status"""
    global doc_processor, processor_initialized
    
    if not processor_initialized:
        return jsonify({
            'initialized': False,
            'message': 'System not initialized. Upload documents to get started.',
            'document_count': {'pdf': 0, 'docx': 0, 'csv': 0}
        })
    
    return jsonify({
        'initialized': True,
        'message': 'System ready',
        'document_count': doc_processor.get_document_count()
    })


@app.route('/api/documents', methods=['GET'])
def get_documents():
    """Get list of uploaded documents"""
    try:
        documents = []
        if os.path.exists(UPLOAD_FOLDER):
            for filename in os.listdir(UPLOAD_FOLDER):
                if allowed_file(filename):
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file_ext = filename.rsplit('.', 1)[1].lower()
                    documents.append({
                        'name': filename,
                        'type': file_ext,
                        'size': os.path.getsize(filepath)
                    })
        
        return jsonify({
            'success': True,
            'documents': documents
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/documents/<filename>', methods=['DELETE'])
def delete_document(filename):
    """Delete a document"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
        
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        # Delete the file
        os.remove(filepath)
        
        # Reinitialize processor
        global doc_processor, processor_initialized
        doc_processor = DocumentProcessor()
        success = doc_processor.initialize()
        processor_initialized = success
        
        return jsonify({
            'success': True,
            'message': f'File "{filename}" deleted successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload (supports multiple files)"""
    if 'files' not in request.files:
        return jsonify({'success': False, 'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    
    if not files or all(f.filename == '' for f in files):
        return jsonify({'success': False, 'error': 'No files selected'}), 400
    
    uploaded_files = []
    errors = []
    
    for file in files:
        if file.filename == '':
            continue
            
        if not allowed_file(file.filename):
            errors.append(f'{file.filename}: Invalid file type')
            continue
        
        try:
            # Save the file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            uploaded_files.append(filename)
        except Exception as e:
            errors.append(f'{file.filename}: {str(e)}')
    
    if not uploaded_files:
        return jsonify({
            'success': False,
            'error': 'No files were uploaded. ' + '; '.join(errors)
        }), 400
    
    try:
        # Incremental update instead of full re-initialization
        global doc_processor, processor_initialized
        
        if not doc_processor:
            doc_processor = DocumentProcessor()
            processor_initialized = True
            
        success_count = 0
        for filename in uploaded_files:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if doc_processor.process_file(filepath):
                success_count += 1
            else:
                errors.append(f"Failed to process {filename}")
        
        if success_count > 0:
            message = f'Successfully uploaded & processed {success_count} file(s)'
            if errors:
                message += f'. Errors: {"; ".join(errors)}'
            
            return jsonify({
                'success': True,
                'message': message,
                'uploaded': uploaded_files,
                'document_count': doc_processor.get_document_count()
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to process files. {"; ".join(errors)}'
            }), 500
            
    except ValueError as e:
        # Check if it's API key error
        if "GROQ_API_KEY" in str(e):
            return jsonify({
                'success': False,
                'error': 'Server configuration error: GROQ_API_KEY not set. Contact administrator.'
            }), 500
        return jsonify({
            'success': False,
            'error': f'Upload processing failed: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Upload processing failed: {str(e)}'
        }), 500


@app.route('/api/query', methods=['POST'])
def query():
    """Handle document query"""
    global doc_processor, processor_initialized
    
    # Initialize if not already done
    if not processor_initialized:
        initialize_processor()
    
    if not processor_initialized or not doc_processor:
        return jsonify({
            'success': False,
            'error': 'System not initialized. Please upload documents first.'
        }), 400
    
    data = request.get_json()
    
    if not data or 'question' not in data:
        return jsonify({
            'success': False,
            'error': 'No question provided'
        }), 400
    
    question = data['question'].strip()
    
    if not question:
        return jsonify({
            'success': False,
            'error': 'Question cannot be empty'
        }), 400
    
    try:
        result = doc_processor.query(question)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Query failed: {str(e)}'
        }), 500


@app.route('/api/initialize', methods=['POST'])
def initialize_endpoint():
    """Manually initialize the system"""
    success = initialize_processor()
    
    if success:
        return jsonify({
            'success': True,
            'message': 'System initialized successfully',
            'document_count': doc_processor.get_document_count()
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Failed to initialize system'
        }), 500



if __name__ == '__main__':
    # Initialize on startup if documents exist
    upload_files = os.listdir(UPLOAD_FOLDER) if os.path.exists(UPLOAD_FOLDER) else []
    if any(allowed_file(f) for f in upload_files):
        print("📁 Found existing documents, initializing...")
        initialize_processor()
    
    # For local development
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
