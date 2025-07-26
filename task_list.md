# Ask ET - Task List

## 🎯 Project Overview
**Product:** Ask ET - AI-powered learning assistant for Emerging Technologies content  
**Goal:** Build a local chatbot for interactive learning from Red Hat blogs and GitHub repositories  
**AI Model:** Google Gemini (gemini-1.5-flash)  
**Timeline:** MVP Day 1 focus, with optional enhancements

---

## 📋 Phase 1: Foundation & Setup (Day 1 - MVP)

### 1.1 Environment Setup
- [x] **1.1.1** Create project directory structure
  - [x] Create `/data` directory for metadata files
  - [x] Create `/ingest` directory for indexing scripts
  - [x] Create `/vector_store` directory for FAISS index
  - [x] Create `/src` directory for main application code

- [x] **1.1.2** Install dependencies
  - [x] Install `langchain`
  - [x] Install `faiss-cpu`
  - [x] Install `openai`
  - [x] Install `tiktoken`
  - [x] Create `requirements.txt` with all dependencies

- [x] **1.1.3** Setup configuration
  - [x] Create `.env` file for API keys
  - [x] Create `config.py` for application settings
  - [x] Setup logging configuration

### 1.2 Data Preparation
- [x] **1.2.1** Prepare existing metadata files
  - [x] Copy `redhat_blogs_complete_list.json` to `/data/blog_metadata.json`
  - [x] Copy `redhat_projects_complete_list.json` to `/data/project_metadata.json`
  - [x] Validate JSON structure and data integrity

- [x] **1.2.2** Data preprocessing
  - [x] Create data loader for blog metadata
  - [x] Create data loader for project metadata
  - [x] Merge and normalize data formats
  - [x] Handle missing or malformed data

### 1.3 Core Ingestion Pipeline
- [x] **1.3.1** Create `ingest/build_index.py`
  - [x] Implement data loading from JSON files
  - [x] Create text chunking logic
  - [x] Implement embedding generation
  - [x] Setup FAISS vector store
  - [x] Add progress tracking and logging

- [x] **1.3.2** Chunking Strategy
  - [x] Define chunk size (e.g., 1000 characters)
  - [x] Implement overlap between chunks
  - [x] Create metadata preservation for chunks
  - [x] Handle different content types (blogs vs projects)

- [x] **1.3.3** Embedding Generation
  - [x] Setup OpenAI API integration
  - [x] Implement batch embedding processing
  - [x] Add error handling and retry logic
  - [x] Create embedding cache to avoid re-processing

### 1.4 Vector Store Setup ✅
- [x] **1.4.1** FAISS Index Creation
  - [x] Initialize FAISS index
  - [x] Add vectors to index
  - [x] Save index to disk (`/vector_store/faiss_index`)
  - [x] Create index metadata file

- [x] **1.4.2** Index Management
  - [x] Create index loading functionality
  - [x] Add index validation
  - [x] Implement index update capabilities
  - [x] Add index statistics and health checks

---

## 📋 Phase 2: Conversational Interface (Day 1 - MVP) ✅

### 2.1 LangChain Integration ✅
- [x] **2.1.1** Setup LangChain RAG Chain
  - [x] Import LangChain dependencies
  - [x] Create ConversationalRetrievalChain
  - [x] Configure retriever with FAISS index
  - [x] Setup conversation memory

- [x] **2.1.2** Query Processing
  - [x] Implement query preprocessing
  - [x] Add query expansion if needed
  - [x] Setup similarity search parameters
  - [x] Configure response generation

### 2.2 CLI Interface ✅
- [x] **2.2.1** Create `cli.py`
  - [x] Setup command-line argument parsing
  - [x] Create interactive chat loop
  - [x] Implement session management
  - [x] Add exit commands and help

- [x] **2.2.2** Chat Session Features
  - [x] Maintain conversation context
  - [x] Display source references
  - [x] Format responses with markdown
  - [x] Add conversation history

- [x] **2.2.3** Response Formatting
  - [x] Format blog references with URLs
  - [x] Format GitHub repository links
  - [x] Add metadata display (dates, authors)
  - [x] Implement response truncation if needed

### 2.3 Testing & Validation ✅
- [x] **2.3.1** Basic Functionality Tests
  - [x] Test data loading
  - [x] Test embedding generation
  - [x] Test vector search
  - [x] Test conversation flow

- [x] **2.3.2** Query Testing
  - [x] Test "Summarize blogs about OpenShift AI"
  - [x] Test "What does Red Hat say about vLLM?"
  - [x] Test "Show GitHub repos mentioned in the last 3 months"
  - [x] Test "Give me 3 blogs to learn model serving on Kubernetes"

---

## 📋 Phase 3: Enhanced Features (Post-MVP)

### 3.1 Content Enhancement
- [ ] **3.1.1** Full Content Scraping
  - [ ] Implement blog content scraping
  - [ ] Add README scraping from GitHub repos
  - [ ] Create content update pipeline
  - [ ] Add content freshness tracking

- [ ] **3.1.2** Advanced Chunking
  - [ ] Implement semantic chunking
  - [ ] Add section-based chunking
  - [ ] Create hierarchical document structure
  - [ ] Add chunk metadata enrichment

### 3.2 Advanced Retrieval
- [ ] **3.2.1** Hybrid Search
  - [ ] Combine dense and sparse retrieval
  - [ ] Implement keyword-based search
  - [ ] Add filtering by date, category, author
  - [ ] Create advanced ranking algorithms

- [ ] **3.2.2** Query Understanding
  - [ ] Add query classification
  - [ ] Implement intent recognition
  - [ ] Create query suggestion system
  - [ ] Add query reformulation

### 3.3 Streamlit UI (Optional)
- [ ] **3.3.1** Web Interface Setup
  - [ ] Install Streamlit
  - [ ] Create basic app structure
  - [ ] Setup chat interface
  - [ ] Add suggested queries panel

- [ ] **3.3.2** UI Features
  - [ ] Create markdown answer panel
  - [ ] Add source display with links
  - [ ] Implement document trace
  - [ ] Add conversation export

---

## 📋 Phase 4: Production Readiness

### 4.1 Performance Optimization
- [ ] **4.1.1** Index Optimization
  - [ ] Optimize FAISS index parameters
  - [ ] Implement index compression
  - [ ] Add index sharding for large datasets
  - [ ] Create index backup and recovery

- [ ] **4.1.2** Response Optimization
  - [ ] Implement response caching
  - [ ] Add query result caching
  - [ ] Optimize embedding generation
  - [ ] Add response time monitoring

### 4.2 Monitoring & Logging
- [ ] **4.2.1** Application Monitoring
  - [ ] Add query logging
  - [ ] Implement performance metrics
  - [ ] Create error tracking
  - [ ] Add usage analytics

- [ ] **4.2.2** Data Quality
  - [ ] Add data validation checks
  - [ ] Implement content freshness alerts
  - [ ] Create data quality reports
  - [ ] Add automated data updates

### 4.3 Documentation
- [ ] **4.3.1** User Documentation
  - [ ] Create README.md
  - [ ] Add installation instructions
  - [ ] Create usage examples
  - [ ] Add troubleshooting guide

- [ ] **4.3.2** Technical Documentation
  - [ ] Document architecture
  - [ ] Add API documentation
  - [ ] Create deployment guide
  - [ ] Add contribution guidelines

---

## 🚀 Quick Start Checklist (Day 1 MVP)

### Immediate Actions (Next 2 hours)
- [ ] **Setup Environment**
  - [ ] Create project structure
  - [ ] Install dependencies
  - [ ] Setup configuration files

- [ ] **Prepare Data**
  - [ ] Copy existing JSON files to `/data`
  - [ ] Validate data structure
  - [ ] Create data loaders

- [ ] **Build Index**
  - [ ] Create `ingest/build_index.py`
  - [ ] Implement chunking and embedding
  - [ ] Generate FAISS index

- [ ] **Create CLI**
  - [ ] Build `cli.py` with LangChain integration
  - [ ] Test basic conversation flow
  - [ ] Validate responses

### Success Criteria (End of Day 1)
- [ ] Can load blog and project metadata
- [ ] Can generate embeddings and create FAISS index
- [ ] Can run CLI interface and ask questions
- [ ] Can get relevant responses with source links
- [ ] Can handle basic conversation context

---

## 📊 Task Status Tracking

| Phase | Task | Status | Priority | Estimated Time |
|-------|------|--------|----------|----------------|
| 1.1 | Environment Setup | 🔴 Not Started | High | 30 min |
| 1.2 | Data Preparation | 🔴 Not Started | High | 45 min |
| 1.3 | Core Ingestion | 🔴 Not Started | High | 2 hours |
| 1.4 | Vector Store | 🔴 Not Started | High | 1 hour |
| 2.1 | LangChain Integration | 🔴 Not Started | High | 1.5 hours |
| 2.2 | CLI Interface | 🔴 Not Started | High | 2 hours |
| 2.3 | Testing | 🔴 Not Started | Medium | 1 hour |

**Legend:**
- 🔴 Not Started
- 🟡 In Progress  
- 🟢 Completed
- 🔵 Blocked

---

## 🎯 Next Steps

1. **Start with Phase 1.1** - Environment Setup
2. **Focus on MVP features** - Get basic CLI working
3. **Test with example queries** - Validate functionality
4. **Iterate and improve** - Add enhancements based on usage

**Total Estimated Time for MVP:** 8-10 hours  
**Target Completion:** End of Day 1 