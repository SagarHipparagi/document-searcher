"""
Document Processor - RAG Logic for Multi-Document Search
Handles PDF, DOCX, and CSV documents with intelligent routing and incremental loading.
Uses TF-IDF for memory-efficient embeddings.
"""

import os
import gc
import glob
import pickle
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Scikit-learn for TF-IDF (memory efficient)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# LangChain imports
from langchain_groq import ChatGroq
from langchain_community.document_loaders import CSVLoader, PyPDFLoader, Docx2txtLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Load environment variables
load_dotenv()

# Memory optimization: Limit total documents
MAX_DOCUMENTS = int(os.getenv('MAX_DOCUMENTS', '10'))

class TfidfRetriever:
    """Memory-efficient retriever using TF-IDF instead of transformer embeddings"""
    
    def __init__(self, documents: List[Document], k: int = 5):
        self.documents = documents
        self.k = k
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Fit on document contents
        self.doc_texts = [doc.page_content for doc in documents]
        self.tfidf_matrix = self.vectorizer.fit_transform(self.doc_texts)
    
    def get_relevant_documents(self, query: str) -> List[Document]:
        """Retrieve top-k most relevant documents"""
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = np.argsort(similarities)[-self.k:][::-1]
        return [self.documents[i] for i in top_indices]
    
    def invoke(self, query: str) -> List[Document]:
        """LangChain compatibility"""
        return self.get_relevant_documents(query)


class DocumentProcessor:
    """Handles document loading, indexing, and querying"""
    
    def __init__(self):
        """Initialize LLM (no heavy embedding model!)"""
        # Get API key
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")
        
        # Initialize LLM only (no heavy embeddings!)
        print("Loading LLM...")
        self.llm = ChatGroq(
            temperature=0.0,
            api_key=self.groq_api_key,
            model="llama-3.3-70b-versatile"
        )
        
        # Storage - Only keep metadata, not full documents (memory optimization)
        self.document_metadata = {'pdf': [], 'docx': [], 'csv': []}  # Store filenames only
        self.documents_by_type = {'pdf': [], 'docx': [], 'csv': []}  # Store Document objects
        self.retrievers = {}
        self.qa_chains = {}
        self.router_chain = None
        
        print("✅ Document processor initialized (TF-IDF mode)")

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
            filename = os.path.basename(filepath)
            for doc in docs:
                doc.metadata['doc_type'] = doc_type
                doc.metadata['filename'] = filename
            
            # Store documents for this type
            self.documents_by_type[doc_type].extend(docs)
            
            # Store only metadata (memory optimization)
            if filename not in self.document_metadata[doc_type]:
                self.document_metadata[doc_type].append(filename)
            
            # Rebuild retriever for this doc type
            self._rebuild_retriever(doc_type)
            
            # Force garbage collection after processing (memory cleanup)
            del docs
            gc.collect()
            
            # Ensure router exists (idempotent)
            if not self.router_chain:
                self.create_router()
                
            return True
        except Exception as e:
            print(f"❌ Error processing file {filepath}: {str(e)}")
            return False

    def _rebuild_retriever(self, doc_type: str):
        """Rebuild TF-IDF retriever and QA chain for a document type"""
        docs = self.documents_by_type[doc_type]
        if not docs:
            return
        
        k = 10 if doc_type == 'csv' else 5
        print(f"🔄 Building TF-IDF retriever for {doc_type} ({len(docs)} docs)")
        
        self.retrievers[doc_type] = TfidfRetriever(docs, k=k)
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
        """Full initialization: load docs, create retrievers, chains, and router"""
        print("🔄 Starting document initialization...")
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
            'pdf': len(self.document_metadata.get('pdf', [])),
            'docx': len(self.document_metadata.get('docx', [])),
            'csv': len(self.document_metadata.get('csv', []))
        }
    
    def get_total_document_count(self) -> int:
        """Get total count of all loaded documents"""
        counts = self.get_document_count()
        return sum(counts.values())
    
    def has_documents(self) -> bool:
        """Check if any documents are loaded"""
        total = sum(len(docs) for docs in self.document_metadata.values())
        return total > 0
