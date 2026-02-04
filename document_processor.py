"""
Document Processor - RAG Logic for Multi-Document Search
Handles PDF, DOCX, and CSV documents with intelligent routing and incremental loading.
"""

import os
import glob
from typing import List, Dict, Optional
from dotenv import load_dotenv

# LangChain imports
from langchain_groq import ChatGroq
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_community.document_loaders import CSVLoader, PyPDFLoader, Docx2txtLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_huggingface import HuggingFaceEmbeddings

# Load environment variables
load_dotenv()

class DocumentProcessor:
    """Handles document loading, indexing, and querying"""
    
    def __init__(self):
        """Initialize embeddings and LLM"""
        # Get API key
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")
        
        # Initialize embeddings model
        print("Loading embeddings model (all-MiniLM-L6-v2)...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            encode_kwargs={"normalize_embeddings": True}
        )
        
        # Initialize LLM
        self.llm = ChatGroq(
            temperature=0.0,
            api_key=self.groq_api_key,
            model="llama-3.3-70b-versatile"
        )
        
        # Storage
        self.documents_by_type = {'pdf': [], 'docx': [], 'csv': []}
        self.vector_stores = {}
        self.retrievers = {}
        self.qa_chains = {}
        self.router_chain = None
        
        print("✅ Document processor initialized")

    def _get_loader_for_file(self, filepath: str):
        """Get appropriate loader for file extension"""
        ext = filepath.split('.')[-1].lower()
        if ext == 'pdf':
            return PyPDFLoader(filepath), 'pdf'
        elif ext == 'docx':
            return Docx2txtLoader(filepath), 'docx'
        elif ext == 'csv':
            return CSVLoader(file_path=filepath), 'csv'
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

    def process_file(self, filepath: str) -> bool:
        """Process a single file incrementally"""
        if not os.path.exists(filepath):
            return False
            
        try:
            print(f"🔄 Processing file: {filepath}")
            loader, doc_type = self._get_loader_for_file(filepath)
            docs = loader.load()
            
            # Add metadata
            for doc in docs:
                doc.metadata['doc_type'] = doc_type
                doc.metadata['filename'] = os.path.basename(filepath)
            
            # Update local storage
            self.documents_by_type[doc_type].extend(docs)
            
            # Incremental Vector Store Update
            self._update_vector_store(doc_type, docs)
            
            # Ensure router exists (idempotent)
            if not self.router_chain:
                self.create_router()
                
            return True
        except Exception as e:
            print(f"❌ Error processing file {filepath}: {str(e)}")
            return False

    def _update_vector_store(self, doc_type: str, new_docs: List[Document]):
        """Add documents to vector store, creating if necessary"""
        # If store exists, add to it
        if doc_type in self.vector_stores:
            print(f"➕ Adding {len(new_docs)} docs to existing {doc_type} store")
            self.vector_stores[doc_type].add_documents(new_docs)
            # Retrievers automatically see new docs in the store usually, 
            # but DocArrayInMemorySearch creates a new index. 
            # Let's verify if we need to recreate the retriever. 
            # Usually 'as_retriever' just wraps the store.
        else:
            # Create new store
            print(f"🆕 Creating new vector store for {doc_type}")
            k = 10 if doc_type == 'csv' else 5
            self.vector_stores[doc_type] = DocArrayInMemorySearch.from_documents(
                new_docs,
                self.embeddings
            )
            self.retrievers[doc_type] = self.vector_stores[doc_type].as_retriever(
                search_kwargs={"k": k}
            )
            # Create QA chain for this new type
            self._create_qa_chain_for_type(doc_type)

    def _create_qa_chain_for_type(self, doc_type: str):
        """Create QA chain for a specific document type"""
        qa_prompt = ChatPromptTemplate.from_template(
            """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, say that you don't know.

Question: {question}

Context: {context}

Answer:"""
        )
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        self.qa_chains[doc_type] = (
            {"context": self.retrievers[doc_type] | format_docs, "question": RunnablePassthrough()}
            | qa_prompt
            | self.llm
            | StrOutputParser()
        )

    # Legacy bulk loader (kept for initialization)
    def load_documents(self, directory: str = "uploads") -> Dict[str, int]:
        """Load all documents from directory"""
        if not os.path.exists(directory):
            os.makedirs(directory)
            return {'pdf': 0, 'docx': 0, 'csv': 0}
        
        counts = {'pdf': 0, 'docx': 0, 'csv': 0}
        
        # Load all supported files
        for ext in ['pdf', 'docx', 'csv']:
            files = glob.glob(f"{directory}/*.{ext}")
            for f in files:
                if self.process_file(f):
                    counts[ext] += 1
                    
        return counts

    def create_vector_stores(self):
        """Deprecated: Logic moved to process_file/_update_vector_store"""
        pass
    
    def create_qa_chains(self):
        """Deprecated: Logic moved to process_file/_create_qa_chain_for_type"""
        pass

    def create_router(self):
        """Create intelligent router"""
        router_template = """Given the user question below, classify it to route to the most relevant document type.

Available document types:
- pdf: General PDF documents (research papers, reports, manuals)
- docx: Word documents (articles, documentation)
- csv: Data files with structured information (sales data, records, tables)

User question: {question}

Respond with ONLY ONE WORD - either 'pdf', 'docx', or 'csv'. Nothing else.
Classification:"""
        
        router_prompt = ChatPromptTemplate.from_template(router_template)
        self.router_chain = router_prompt | self.llm | StrOutputParser()
    
    def initialize(self):
        """Full initialization: load docs, create stores, chains, and router"""
        print("🔄 Starting document initialization...")
        # Just use load_documents which now uses process_file internally
        counts = self.load_documents()
        print(f"📚 Loaded documents: {counts}")
        
        if sum(counts.values()) == 0:
            print("❌ No documents found")
            return False
            
        print("✅ Initialization complete!")
        return True
    
    def query(self, question: str) -> Dict[str, any]:
        """Query the documents"""
        if not self.qa_chains:
            return {
                'success': False,
                'error': 'No documents loaded. Please upload documents first.'
            }
        
        try:
            # Ensure router exists
            if not self.router_chain:
                self.create_router()

            # Route to appropriate document type
            doc_type = self.router_chain.invoke({"question": question}).strip().lower()
            
            # Validate
            if doc_type not in self.qa_chains:
                # Fallback to first available chain
                doc_type = list(self.qa_chains.keys())[0]
            
            # Get answer
            answer = self.qa_chains[doc_type].invoke(question)
            
            return {
                'success': True,
                'answer': answer,
                'doc_type': doc_type,
                'question': question
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_document_count(self) -> Dict[str, int]:
        """Get count of loaded documents by type"""
        return {
            'pdf': len(self.documents_by_type.get('pdf', [])),
            'docx': len(self.documents_by_type.get('docx', [])),
            'csv': len(self.documents_by_type.get('csv', []))
        }
    
    def has_documents(self) -> bool:
        """Check if any documents are loaded"""
        total = sum(len(docs) for docs in self.documents_by_type.values())
        return total > 0
