# 🔍 Document Search Engine

A modern, Apple-inspired web application for intelligent document search using RAG (Retrieval-Augmented Generation).

## ✨ Features

- 📄 **Multi-format Support**: Upload and search PDF, DOCX, and CSV files
- 🤖 **AI-Powered Search**: Natural language queries with context-aware answers
- 🎨 **Apple-Inspired UI**: Clean, minimal design with dark/light mode
- ⚡ **Fast**: In-memory vector stores for quick retrieval
- 🔒 **Local-First**: All processing happens on your machine

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Groq API Key ([Get one free](https://console.groq.com))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/document-search-engine.git
cd document-search-engine
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
# Copy the example .env file
cp .env.example .env

# Edit .env and add your Groq API key
# GROQ_API_KEY=your_api_key_here
```

4. **Run the application**
```bash
python app.py
```

5. **Open your browser**
```
http://localhost:5000
```

## 📖 Usage

1. **Upload Documents**: Drag and drop PDF, DOCX, or CSV files
2. **Ask Questions**: Type natural language questions about your documents
3. **Get Answers**: AI-powered responses with source attribution
4. **Toggle Theme**: Switch between light and dark mode

## 🛠️ Tech Stack

- **Backend**: Flask
- **AI**: LangChain + Groq (Llama 3.3 70B)
- **Embeddings**: HuggingFace (all-mpnet-base-v2)
- **Vector Store**: DocArray (in-memory)
- **Frontend**: Vanilla HTML/CSS/JavaScript

## 📁 Project Structure

```
document-search-engine/
├── app.py                    # Flask API server
├── document_processor.py     # RAG logic
├── requirements.txt          # Python dependencies
├── .env.example             # Example environment variables
├── static/
│   ├── index.html           # Main HTML
│   ├── css/style.css        # Styling
│   ├── js/app.js            # Frontend logic
│   └── favicon.png          # Favicon
└── uploads/                 # User uploaded files
```

## 🔑 Environment Variables

Create a `.env` file with:

```env
GROQ_API_KEY=your_groq_api_key_here
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com)
- Powered by [Groq](https://groq.com)
- Embeddings by [HuggingFace](https://huggingface.co)

---

**Made with ❤️ using Flask, LangChain, and Groq**
