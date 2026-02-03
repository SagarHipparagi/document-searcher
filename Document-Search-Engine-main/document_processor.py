"""
Document Processor - RAG Logic for Multi-Document Search
Handles PDF, DOCX, and CSV documents with intelligent routing
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
        print("Loading embeddings model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2",
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
    
    def load_documents(self, directory: str = "uploads") -> Dict[str, int]:
        """Load all documents from directory"""
        if not os.path.exists(directory):
            os.makedirs(directory)
            return {'pdf': 0, 'docx': 0, 'csv': 0}
        
        counts = {'pdf': 0, 'docx': 0, 'csv': 0}
        
        # Load PDFs
        for pdf_file in glob.glob(f"{directory}/*.pdf"):
            loader = PyPDFLoader(pdf_file)
            docs = loader.load()
            for doc in docs:
                doc.metadata['doc_type'] = 'pdf'
                doc.metadata['filename'] = os.path.basename(pdf_file)
            self.documents_by_type['pdf'].extend(docs)
            counts['pdf'] += 1
        
        # Load DOCX
        for docx_file in glob.glob(f"{directory}/*.docx"):
            loader = Docx2txtLoader(docx_file)
            docs = loader.load()
            for doc in docs:
                doc.metadata['doc_type'] = 'docx'
                doc.metadata['filename'] = os.path.basename(docx_file)
            self.documents_by_type['docx'].extend(docs)
            counts['docx'] += 1
        
        # Load CSV
        for csv_file in glob.glob(f"{directory}/*.csv"):
            loader = CSVLoader(file_path=csv_file)
            docs = loader.load()
            for doc in docs:
                doc.metadata['doc_type'] = 'csv'
                doc.metadata['filename'] = os.path.basename(csv_file)
            self.documents_by_type['csv'].extend(docs)
            counts['csv'] += 1
        
        return counts
    
    def create_vector_stores(self):
        """Create vector stores for each document type"""
        # PDF vector store
        if self.documents_by_type['pdf']:
            self.vector_stores['pdf'] = DocArrayInMemorySearch.from_documents(
                self.documents_by_type['pdf'],
                self.embeddings
            )
            self.retrievers['pdf'] = self.vector_stores['pdf'].as_retriever(
                search_kwargs={"k": 5}
            )
        
        # DOCX vector store
        if self.documents_by_type['docx']:
            self.vector_stores['docx'] = DocArrayInMemorySearch.from_documents(
                self.documents_by_type['docx'],
                self.embeddings
            )
            self.retrievers['docx'] = self.vector_stores['docx'].as_retriever(
                search_kwargs={"k": 5}
            )
        
        # CSV vector store
        if self.documents_by_type['csv']:
            self.vector_stores['csv'] = DocArrayInMemorySearch.from_documents(
                self.documents_by_type['csv'],
                self.embeddings
            )
            self.retrievers['csv'] = self.vector_stores['csv'].as_retriever(
                search_kwargs={"k": 10}
            )
    
    def create_qa_chains(self):
        """Create QA chains for each document type"""
        qa_prompt = ChatPromptTemplate.from_template(
            """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, say that you don't know.

Question: {question}

Context: {context}

Answer:"""
        )
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        for doc_type, retriever in self.retrievers.items():
            self.qa_chains[doc_type] = (
                {"context": retriever | format_docs, "question": RunnablePassthrough()}
                | qa_prompt
                | self.llm
                | StrOutputParser()
            )
    
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
        counts = self.load_documents()
        print(f"📚 Loaded documents: {counts}")
        
        if sum(counts.values()) == 0:
            print("❌ No documents found")
            return False
        
        print("🔨 Creating vector stores...")
        self.create_vector_stores()
        print(f"✅ Vector stores created for: {list(self.vector_stores.keys())}")
        
        print("⚙️  Creating QA chains...")
        self.create_qa_chains()
        print(f"✅ QA chains created for: {list(self.qa_chains.keys())}")
        
        print("🧭 Creating router...")
        self.create_router()
        print("✅ Router created")
        
        print("🎉 Initialization complete!")
        return True
    
    def query(self, question: str) -> Dict[str, any]:
        """Query the documents"""
        if not self.router_chain or not self.qa_chains:
            return {
                'success': False,
                'error': 'No documents loaded. Please upload documents first.'
            }
        
        try:
            # Route to appropriate document type
            doc_type = self.router_chain.invoke({"question": question}).strip().lower()
            
            # Validate
            if doc_type not in self.qa_chains:
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
        return total > 0 and len(self.qa_chains) > 0
