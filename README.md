# Ask ET - AI-powered Learning Assistant

An AI-powered chatbot for interactive learning from Emerging Technologies content, built with Google Gemini and LangChain.

## 🚀 Features

- **RAG-powered Chatbot**: Uses Retrieval-Augmented Generation for accurate responses
- **Red Hat Content**: Indexed 114+ blog posts and 33+ projects from Red Hat Emerging Technologies
- **Google Gemini Integration**: Powered by Google's Gemini 1.5 Flash model
- **Local Vector Store**: FAISS-based vector database for fast similarity search
- **CLI Interface**: Simple command-line interface for interactive learning

## 📋 Prerequisites

- Python 3.8+
- Google API Key (free from [Google AI Studio](https://makersuite.google.com/app/apikey))

## 🛠️ Installation

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd next.redhat.com
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Get Google API Key**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key (free tier available)
   - Copy the API key

4. **Configure environment**:
   ```bash
   # Create .env file
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```

## 🏗️ Project Structure

```
next.redhat.com/
├── data/                    # Metadata files
│   ├── blog_metadata.json   # Blog posts data
│   └── project_metadata.json # Projects data
├── ingest/                  # Indexing pipeline
│   ├── build_index.py       # Main indexing script
│   └── test_*.py           # Test scripts
├── src/                     # Application code
│   ├── data_loader.py      # Data loading utilities
│   └── logger.py           # Logging configuration
├── vector_store/           # FAISS index storage
├── config.py               # Configuration settings
└── requirements.txt        # Python dependencies
```

## 🔧 Usage

### 1. Build the Index

First, build the vector index from your data:

```bash
python ingest/build_index.py
```

This will:
- Load blog and project metadata
- Create text chunks
- Generate embeddings using Gemini
- Build and save FAISS index

### 2. Test the Setup

Run tests to verify everything is working:

```bash
# Test data loading and chunking
python ingest/simple_test.py

# Test Gemini integration
python ingest/test_gemini_simple.py
```

### 3. Start Chatting

Once the index is built, you can start the chatbot:

```bash
python src/cli.py
```

## 📊 Data Statistics

- **Blog Posts**: 114 articles from Emerging Technologies
- **Projects**: 33 open-source projects
- **Categories**: AI, Edge Computing, Developer Productivity, Hybrid Cloud, Sustainability, Trust
- **Content Types**: Technical articles, project descriptions, GitHub repositories

## 🎯 Example Queries

- "Summarize blogs about OpenShift AI"
- "What does Red Hat say about vLLM?"
- "Show GitHub repos mentioned in the last 3 months"
- "Give me 3 blogs to learn model serving on Kubernetes"

## 🔧 Configuration

Key configuration options in `config.py`:

- `CHUNK_SIZE`: Text chunk size (default: 1000 characters)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200 characters)
- `GEMINI_MODEL`: Gemini model to use (default: gemini-1.5-flash)
- `TOP_K_RESULTS`: Number of similar documents to retrieve (default: 5)

## 🚧 Development Status

- ✅ **Phase 1.1**: Environment Setup
- ✅ **Phase 1.2**: Data Preparation
- ✅ **Phase 1.3**: Core Ingestion Pipeline
- ✅ **Phase 1.4**: Vector Store Setup
- ✅ **Phase 2**: Conversational Interface
- ⏳ **Phase 3**: Enhanced Features
- ⏳ **Phase 4**: Production Readiness

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Emerging Technologies for the content
- Google for the Gemini AI model
- LangChain for the RAG framework
- FAISS for vector similarity search
