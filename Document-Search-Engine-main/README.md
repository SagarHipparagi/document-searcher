# 🔍 My Multi-Document Search Engine

I built this to stop jumping between spreadsheets, PDFs, and Word docs every time I need a simple answer. Now I just ask a question, and the system figures out where to look (CSV, PDF, or DOCX) and gives me a straight answer with sources. It’s fast, local for retrieval, and easy to extend.

-I used sentence-transformers/all-mpnet-base-v2 (768 dimensions) embedding model from HuggingFace to create vectors
-I used opensource model openai/gpt-oss-20b:free from Openrouter.

If you're just getting started, you can follow exactly what I do:
- I first install the requirements from requirements.txt
- Then I open the notebook `miniLM.ipynb` and run all cells
- Finally, I ask real questions like “Who won the Singapore Grand Prix 2025?” or “Summarize the PDF report”

Why I built this (in one line): I wanted a single place to ask questions across different document types without reformatting or switching tools.

## Data source

I included the reports in word and pdf of the events happened after the the openai/gpt-oss-20b:free model is trained, which means it doesn't know these events.It is beacause to check this engine's capability to retrieve unknown information from documents.
**The knowledge cutoff date for OpenAI's GPT-OSS models—gpt-oss-120b and gpt-oss-20b—is June 2024**
1)PDF document: I used the report of Iphone 17 series launch on 19th September 2025
2)Word document: I used the report of F1 Singapore Grand Prix 2025 held on 5th October 2025


## Test Results

Please refer to the testresults.md file to see the results.
Results were accurate!!!

## What it does (in plain English)

- **Multi-Format Support**: Handles PDF, DOCX, and CSV files
- **Smart Routing**: Automatically determines which document type to search based on your query
- **LangChain Framework**: Built entirely using LangChain's chains and routers
- **Vector Search**: Uses HuggingFace embeddings for semantic search
- **Conversational AI**: Powered by OpenRouter API for natural language responses


## How I put it together

### Components

1. **Document Loaders**
   - `PyPDFLoader` for PDF files
   - `Docx2txtLoader` for Word documents
   - `CSVLoader` for CSV/Excel data

2. **Vector Stores**
   - Separate `DocArrayInMemorySearch` store for each document type
   - Uses `sentence-transformers/all-mpnet-base-v2` embeddings

3. **Router System**
   - `LLMRouterChain` analyzes queries and routes to appropriate document type
   - `MultiRouteChain` manages multiple QA chains
   - Destination chains for PDF, DOCX, and CSV

4. **QA Chains**
   - `RetrievalQA` chains with "stuff" strategy
   - Dedicated chain for each document type
   - Returns source documents for transparency

## Installation (what I run)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your API key:
```
OPENROUTER_API_KEY=your_api_key_here
```

## How I use it day-to-day

### Option 1: Jupyter Notebook (when I’m exploring)

1. Place your documents (PDF, DOCX, CSV) in the project directory

2. Open and run `miniLM.ipynb`

3. Use the query function:
```python
query_documents("Your question here")
```

### Option 2: Python Script (when I’m automating)

1. Place your documents in the project directory

2. Run the script:
```bash
python document_search.py
```

3. Use in your code:
```python
from document_search import MultiDocumentSearchEngine

engine = MultiDocumentSearchEngine(directory="./your_documents")
engine.initialize()
answer = engine.query("Your question here")
```

### Examples I actually ask

**For CSV/Excel data:**
- "Analyze any three orders and give a short summary"
- "What is the total sales amount?"
- "Which customer has the highest profit?"
- "Show me the top 3 products by sales"

**For PDF documents:**
- "What are the main topics discussed in the PDF?"
- "Summarize the key findings from the report"

**For Word documents:**
- "What are the main points in the Word document?"
- "Extract the action items from the memo"

## What happens under the hood

1. **Document Loading**: All documents in the directory are loaded and categorized by type

2. **Embedding**: Each document is converted to vector embeddings using HuggingFace models

3. **Vector Storage**: Documents are stored in type-specific vector stores for efficient retrieval

4. **Query Routing**: When you ask a question:
   - The router analyzes your query
   - Determines the most relevant document type
   - Routes to the appropriate QA chain

5. **Retrieval & Answer**: 
   - Relevant documents are retrieved using semantic search
   - LLM generates a natural language answer
   - Source documents are provided for verification

## Tech details (at a glance)

- **Embeddings Model**: `sentence-transformers/all-mpnet-base-v2` (768 dimensions)
- **LLM**: OpenRouter API (configurable model)
- **Vector Store**: DocArray In-Memory Search
- **Framework**: LangChain (chains, routers, retrievers)

## Project layout

```
docu-searchengine/
├── miniLM.ipynb          # Main notebook with implementation
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── .env                 # API keys (not in repo)
└── [your documents]     # PDF, DOCX, CSV files
```

## How the router decides

The router uses these descriptions to classify queries:

- **PDF**: Reports, articles, papers, documentation, manuals, textual information
- **DOCX**: Letters, memos, proposals, formatted documents, business documents
- **CSV**: Tabular data, sales records, orders, numerical data, statistics, transactions

## If I want to extend it

To add new document types:

1. Add the appropriate loader to `requirements.txt`
2. Update the `load_documents_by_type()` function
3. Add a new description to the router
4. Create a corresponding QA chain

## Notes I keep in mind

- The system automatically handles multiple files of the same type
- Vector stores are created in-memory (not persisted)
- Router uses LLM to intelligently classify queries
- All processing is done locally except LLM API calls

## License

MIT License - Feel free to use and modify

