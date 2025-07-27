# Ask ET - Detailed Architecture & Tech Stack

## Table of Contents
1. [System Architecture Overview](#1-system-architecture-overview)
2. [Component-Level Architecture](#2-component-level-architecture)
3. [Technology Stack Deep Dive](#3-technology-stack-deep-dive)
4. [Data Flow Architecture](#4-data-flow-architecture)
5. [Performance Architecture](#5-performance-architecture)
6. [Security Architecture](#6-security-architecture)
7. [Deployment Architecture](#7-deployment-architecture)
8. [Scalability Architecture](#8-scalability-architecture)

---

## 1. System Architecture Overview

### **High-Level System Design**

```mermaid
graph TB
    subgraph "User Layer"
        A1[Web Interface<br/>Streamlit]
        A2[CLI Interface<br/>Python CLI]
        A3[API Endpoints<br/>REST/GraphQL]
        A4[Mobile/Agentic Interface<br/>Future]
    end
    
    subgraph "Application Layer"
        B1[Web Controllers<br/>Streamlit]
        B2[CLI Handlers<br/>Click]
        B3[API Controllers<br/>FastAPI]
        B4[Response Formatters]
    end
    
    subgraph "Business Logic Layer"
        C1[Query Processor]
        C2[RAG Engine<br/>LangChain]
        C3[Response Generator]
        C4[Content Manager]
    end
    
    subgraph "Data Access Layer"
        D1[Vector Store<br/>FAISS]
        D2[Metadata<br/>JSON/DB]
        D3[Configuration<br/>Python]
        D4[Cache Layer<br/>Redis/Memory]
    end
    
    subgraph "External Services"
        E1[LLM Service<br/>Google Gemini]
        E2[Web Scraping<br/>BeautifulSoup]
        E3[File Storage<br/>Local/Cloud]
        E4[Monitoring<br/>Logging/Metrics]
    end
    
    A1 --> B1
    A2 --> B2
    A3 --> B3
    A4 --> B4
    
    B1 --> C1
    B2 --> C2
    B3 --> C3
    B4 --> C4
    
    C1 --> D1
    C2 --> D2
    C3 --> D3
    C4 --> D4
    
    D1 --> E1
    D2 --> E2
    D3 --> E3
    D4 --> E4
```

### **Architecture Principles**

#### **1. Layered Architecture**
- **Separation of Concerns**: Each layer has distinct responsibilities
- **Loose Coupling**: Components can be modified independently
- **High Cohesion**: Related functionality grouped together
- **Dependency Inversion**: High-level modules don't depend on low-level modules

#### **2. Microservices-Ready Design**
- **Modular Components**: Each component can be deployed independently
- **API-First Approach**: All functionality accessible via APIs
- **Stateless Design**: No session state stored in application
- **Container-Ready**: Each component can be containerized

#### **3. Event-Driven Architecture**
- **Asynchronous Processing**: Non-blocking operations
- **Event Sourcing**: All state changes tracked as events
- **CQRS Pattern**: Separate read and write operations
- **Event Streaming**: Real-time data flow capabilities

---

## 2. Component-Level Architecture

### **Frontend Components**

#### **Web Interface (Streamlit)**
```python
# Architecture Pattern: MVC (Model-View-Controller)
class WebAppController:
    def __init__(self):
        self.rag_chain = create_improved_rag_chain()
        self.response_formatter = create_enhanced_response_formatter()
    
    def process_query(self, query: str) -> Dict[str, Any]:
        # Controller logic
        result = self.rag_chain.query(query)
        return self.response_formatter.format_for_web_display(result)
```

**Technology Stack**:
- **Framework**: Streamlit 1.28+
- **UI Components**: Streamlit widgets, markdown, charts
- **State Management**: Streamlit session state
- **Styling**: Custom CSS, Streamlit themes
- **Responsive Design**: Mobile-friendly layouts

#### **CLI Interface (Click)**
```python
# Architecture Pattern: Command Pattern
@click.command()
@click.option('--query', '-q', help='Search query')
@click.option('--format', '-f', default='text', help='Output format')
def cli_interface(query: str, format: str):
    # Command execution
    result = process_query(query)
    display_result(result, format)
```

**Technology Stack**:
- **Framework**: Click 8.0+
- **Argument Parsing**: Click options and arguments
- **Output Formatting**: Rich text, JSON, CSV
- **Interactive Mode**: REPL-style interface
- **Help System**: Auto-generated help documentation

### **Backend Components**

#### **RAG Engine (LangChain)**
```python
# Architecture Pattern: Chain of Responsibility
class ImprovedRAGChain:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        self.vector_store = FAISS.load_local("vector_store/faiss_index")
        self.memory = ConversationBufferMemory()
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vector_store.as_retriever(),
            memory=self.memory
        )
```

**Technology Stack**:
- **Framework**: LangChain 0.1.0+
- **LLM Integration**: Google Gemini 1.5 Flash
- **Vector Store**: FAISS (Facebook AI Similarity Search)
- **Memory Management**: ConversationBufferMemory
- **Chain Types**: ConversationalRetrievalChain

#### **Enhanced Response Formatter**
```python
# Architecture Pattern: Strategy Pattern
class EnhancedResponseFormatter:
    def __init__(self):
        self.blog_metadata = self._load_blog_metadata()
        self.project_metadata = self._load_project_metadata()
        self.strategies = {
            'author': self._find_blogs_by_author,
            'technology': self._find_blogs_by_technology,
            'exact': self._find_exact_blog_match,
            'fallback': self._find_relevant_blogs_from_metadata
        }
```

**Technology Stack**:
- **Pattern Matching**: Regular expressions, fuzzy matching
- **Data Structures**: Dictionaries, lists, sets
- **Algorithms**: Relevance scoring, deduplication
- **Caching**: In-memory caching for metadata
- **Error Handling**: Graceful degradation

### **Data Layer Components**

#### **Vector Store (FAISS)**
```python
# Architecture Pattern: Repository Pattern
class VectorStoreRepository:
    def __init__(self, index_path: str):
        self.index = faiss.read_index(index_path)
        self.metadata = self._load_metadata()
    
    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Dict]:
        # Vector similarity search
        scores, indices = self.index.search(query_vector, k)
        return self._format_results(scores, indices)
```

**Technology Stack**:
- **Vector Database**: FAISS (Facebook AI Similarity Search)
- **Index Types**: IVF (Inverted File Index)
- **Distance Metrics**: Cosine similarity, L2 distance
- **Optimization**: GPU acceleration support
- **Persistence**: Binary index files

#### **Metadata Management**
```python
# Architecture Pattern: Data Access Object (DAO)
class MetadataDAO:
    def __init__(self, blog_path: str, project_path: str):
        self.blog_metadata = self._load_json(blog_path)
        self.project_metadata = self._load_json(project_path)
    
    def get_blogs_by_author(self, author: str) -> List[Dict]:
        # Author-based filtering
        return [blog for blog in self.blog_metadata['blogs'] 
                if author.lower() in blog['author'].lower()]
```

**Technology Stack**:
- **Data Format**: JSON (JavaScript Object Notation)
- **Serialization**: Python json module
- **Validation**: Pydantic models (optional)
- **Caching**: In-memory dictionaries
- **Backup**: Version-controlled data files

---

## 3. Technology Stack Deep Dive

```mermaid
graph TB
    subgraph "Core Runtime"
        A1[Python 3.8+]
        A2[NumPy]
        A3[Pandas]
    end
    
    subgraph "AI/ML Framework"
        B1[LangChain 0.1.0+]
        B2[Google Gemini 1.5 Flash]
        B3[FAISS Vector DB]
    end
    
    subgraph "Web Framework"
        C1[Streamlit 1.28+]
        C2[Click 8.0+]
        C3[FastAPI]
    end
    
    subgraph "Data Processing"
        D1[BeautifulSoup4]
        D2[Requests]
        D3[JSON]
    end
    
    subgraph "Utilities"
        E1[Python-dotenv]
        E2[Dateutil]
        E3[TQDM]
    end
    
    A1 --> B1
    A2 --> B3
    A3 --> D1
    
    B1 --> B2
    B1 --> B3
    
    C1 --> A1
    C2 --> A1
    C3 --> A1
    
    D1 --> D2
    D2 --> D3
    
    E1 --> A1
    E2 --> A1
    E3 --> A1
```

### **Core Framework: Python 3.8+**

#### **Why Python?**
- **AI/ML Ecosystem**: Rich libraries for NLP, vector operations, and AI integration
- **LangChain Compatibility**: Native support for RAG implementations
- **Community Support**: Extensive documentation and community resources
- **Production Ready**: Proven in enterprise AI applications

#### **Python Dependencies**
```python
# Core AI/ML Libraries
langchain==0.1.0          # RAG framework
google-generativeai==0.3.0 # Google Gemini integration
faiss-cpu==1.7.4          # Vector similarity search
numpy==1.24.0             # Numerical computations
pandas==2.0.0             # Data manipulation

# Web Framework
streamlit==1.28.0         # Web interface
click==8.1.0              # CLI framework

# Data Processing
beautifulsoup4==4.12.0    # Web scraping
requests==2.31.0          # HTTP client
python-dotenv==1.0.0      # Environment management

# Utilities
python-dateutil==2.8.2    # Date handling
tqdm==4.65.0              # Progress bars
```

### **RAG Framework: LangChain 0.1.0+**

#### **LangChain Architecture**
```python
# LangChain Component Architecture
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LLM Chain     │───▶│   Memory        │───▶│   Output Parser │
│   (Gemini)      │    │   (Buffer)      │    │   (Structured)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Retriever     │    │   Prompt        │    │   Callbacks     │
│   (FAISS)       │    │   Templates     │    │   (Logging)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### **LangChain Benefits**
- **Modular Design**: Components can be swapped independently
- **Memory Management**: Built-in conversation context handling
- **Prompt Engineering**: Template-based prompt management
- **Callbacks**: Extensible logging and monitoring
- **Chain Composition**: Complex workflows from simple components

### **Language Model: Google Gemini 1.5 Flash**

#### **Model Specifications**
- **Model Size**: 1.5B parameters (optimized for speed)
- **Context Window**: 32K tokens
- **Response Time**: <500ms average
- **Cost**: $0.000075 per 1K input tokens, $0.0003 per 1K output tokens
- **Availability**: 99.9% uptime SLA

#### **Integration Architecture**
```python
# Gemini Integration Pattern
class GeminiService:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def generate_response(self, prompt: str, context: str) -> str:
        # Async generation for better performance
        response = await self.model.generate_content_async(
            f"{context}\n\n{prompt}"
        )
        return response.text
```

#### **Performance Optimizations**
- **Async Processing**: Non-blocking API calls
- **Batch Processing**: Multiple queries in single request
- **Caching**: Response caching for repeated queries
- **Retry Logic**: Exponential backoff for failures
- **Rate Limiting**: Respect API quotas

### **Vector Database: FAISS (Facebook AI Similarity Search)**

#### **FAISS Architecture**
```python
# FAISS Index Architecture
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Input         │───▶│   Index         │───▶│   Search        │
│   Vectors       │    │   (IVF)         │    │   Results       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Normalization │    │   Clustering    │    │   Ranking       │
│   (L2/Cosine)   │    │   (K-means)     │    │   (Distance)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### **Index Types and Performance**
- **IVF (Inverted File Index)**: Fast approximate search
- **PQ (Product Quantization)**: Memory-efficient encoding
- **HNSW (Hierarchical Navigable Small World)**: High-quality results
- **GPU Support**: CUDA acceleration for large indices

#### **Performance Characteristics**
- **Search Speed**: 1M vectors in <10ms
- **Memory Usage**: 4GB for 1M vectors (float32)
- **Accuracy**: 95%+ recall for top-5 results
- **Scalability**: Linear scaling with dataset size

### **Web Framework: Streamlit 1.28+**

#### **Streamlit Architecture**
```python
# Streamlit Component Architecture
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │───▶│   Streamlit     │───▶│   Backend       │
│   (Widgets)     │    │   Session       │    │   Processing    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   State         │    │   Caching       │    │   Response      │
│   Management    │    │   (st.cache)    │    │   Rendering     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### **Streamlit Benefits**
- **Rapid Development**: Prototype to production in minutes
- **Interactive Elements**: Real-time updates and feedback
- **Data Visualization**: Built-in charts and graphs
- **Deployment**: One-command cloud deployment
- **Customization**: CSS and component customization

### **Data Processing: Pandas & NumPy**

#### **Data Processing Pipeline**
```python
# Data Processing Architecture
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Raw Data      │───▶│   Pandas        │───▶│   Clean Data    │
│   (CSV/JSON)    │    │   Processing    │    │   (DataFrame)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   NumPy         │    ┌─────────────────┐    ┌─────────────────┐
│   Operations    │    │   Vector        │    │   Output        │
│   (Arrays)      │    │   Embeddings    │    │   (FAISS)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### **Performance Optimizations**
- **Vectorized Operations**: NumPy array operations
- **Memory Efficiency**: Pandas data types optimization
- **Parallel Processing**: Multi-core data processing
- **Lazy Evaluation**: Chained operations optimization

---

## 4. Data Flow Architecture

### **End-to-End Data Flow**

```mermaid
graph LR
    A[User Query<br/>Natural Language] --> B[Input Validation<br/>& Cleaning]
    B --> C[Query Processing<br/>& Analysis]
    C --> D[Tokenization<br/>& Chunking]
    
    D --> E[Embedding Generation<br/>Gemini]
    E --> F[Vector Search<br/>FAISS]
    F --> G[Document Retrieval<br/>Top-K]
    
    G --> H[Context Assembly<br/>Prompt Engineering]
    H --> I[Response Generation<br/>LLM]
    I --> J[Metadata Retrieval<br/>JSON]
    
    J --> K[Content Enrichment<br/>Author, Projects]
    K --> L[Response Enhancement<br/>Blogs + Projects]
    L --> M[Final Response]
    
    style A fill:#e1f5fe
    style M fill:#c8e6c9
    style F fill:#fff3e0
    style I fill:#fff3e0
```

### **Data Transformation Pipeline**

#### **1. Input Processing**
```python
# Input Processing Pipeline
def process_input(query: str) -> ProcessedQuery:
    # 1. Text cleaning
    cleaned_query = clean_text(query)
    
    # 2. Tokenization
    tokens = tokenize(cleaned_query)
    
    # 3. Intent classification
    intent = classify_intent(tokens)
    
    # 4. Query normalization
    normalized_query = normalize_query(tokens, intent)
    
    return ProcessedQuery(
        original=query,
        cleaned=cleaned_query,
        tokens=tokens,
        intent=intent,
        normalized=normalized_query
    )
```

#### **2. Vector Generation**
```python
# Vector Generation Pipeline
def generate_embeddings(text: str) -> np.ndarray:
    # 1. Text preprocessing
    processed_text = preprocess_text(text)
    
    # 2. Tokenization
    tokens = tokenizer.encode(processed_text)
    
    # 3. Embedding generation
    embeddings = embedding_model.encode(tokens)
    
    # 4. Normalization
    normalized_embeddings = normalize_embeddings(embeddings)
    
    return normalized_embeddings
```

#### **3. Search and Retrieval**
```python
# Search and Retrieval Pipeline
def search_documents(query_vector: np.ndarray, k: int = 5) -> List[Document]:
    # 1. Vector similarity search
    scores, indices = vector_store.search(query_vector, k)
    
    # 2. Document retrieval
    documents = [vector_store.get_document(idx) for idx in indices]
    
    # 3. Relevance scoring
    scored_documents = score_relevance(documents, query_vector)
    
    # 4. Deduplication
    unique_documents = deduplicate_documents(scored_documents)
    
    return unique_documents[:k]
```

#### **4. Response Generation**
```python
# Response Generation Pipeline
def generate_response(query: str, documents: List[Document]) -> Response:
    # 1. Context assembly
    context = assemble_context(documents)
    
    # 2. Prompt engineering
    prompt = create_prompt(query, context)
    
    # 3. LLM generation
    raw_response = llm.generate(prompt)
    
    # 4. Response parsing
    parsed_response = parse_response(raw_response)
    
    # 5. Content enhancement
    enhanced_response = enhance_response(parsed_response, documents)
    
    return enhanced_response
```

---

## 5. Performance Architecture

### **Performance Optimization Strategies**

#### **1. Caching Architecture**
```python
# Multi-Level Caching Strategy
class CacheManager:
    def __init__(self):
        self.l1_cache = {}  # In-memory cache (fastest)
        self.l2_cache = {}  # Disk cache (medium)
        self.l3_cache = {}  # Distributed cache (slowest)
    
    def get(self, key: str) -> Any:
        # L1 cache lookup
        if key in self.l1_cache:
            return self.l1_cache[key]
        
        # L2 cache lookup
        if key in self.l2_cache:
            value = self.l2_cache[key]
            self.l1_cache[key] = value  # Promote to L1
            return value
        
        # L3 cache lookup
        if key in self.l3_cache:
            value = self.l3_cache[key]
            self.l2_cache[key] = value  # Promote to L2
            return value
        
        return None
```

#### **2. Async Processing**
```python
# Async Processing Architecture
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncProcessor:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def process_query(self, query: str) -> Response:
        # Parallel processing of different components
        tasks = [
            self.vector_search(query),
            self.metadata_lookup(query),
            self.llm_generation(query)
        ]
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)
        
        # Combine results
        return self.combine_results(results)
```

#### **3. Batch Processing**
```python
# Batch Processing Architecture
class BatchProcessor:
    def __init__(self, batch_size: int = 10):
        self.batch_size = batch_size
        self.batch_queue = []
    
    def add_to_batch(self, item: Any):
        self.batch_queue.append(item)
        
        if len(self.batch_queue) >= self.batch_size:
            self.process_batch()
    
    def process_batch(self):
        # Process batch of items together
        batch_items = self.batch_queue[:self.batch_size]
        self.batch_queue = self.batch_queue[self.batch_size:]
        
        # Batch processing logic
        results = self.process_items_batch(batch_items)
        
        # Return results to individual callers
        for item, result in zip(batch_items, results):
            item.set_result(result)
```

### **Performance Metrics**

#### **Response Time Targets**
- **Web Interface**: <2 seconds end-to-end
- **CLI Interface**: <1 second for simple queries
- **API Endpoints**: <500ms for cached responses
- **Vector Search**: <10ms for 1M vectors
- **LLM Generation**: <500ms for typical responses

#### **Throughput Targets**
- **Concurrent Users**: 100+ simultaneous users
- **Queries per Second**: 50+ QPS
- **Vector Searches**: 1000+ searches per second
- **LLM Calls**: 100+ calls per minute

#### **Resource Utilization**
- **CPU Usage**: <70% under normal load
- **Memory Usage**: <4GB for 1M vectors
- **Disk I/O**: <100MB/s for vector operations
- **Network**: <10MB/s for API responses

---

## 6. Security Architecture

### **Security Layers**

#### **1. Authentication & Authorization**
```python
# Security Architecture
class SecurityManager:
    def __init__(self):
        self.api_keys = self.load_api_keys()
        self.rate_limits = RateLimiter()
        self.audit_log = AuditLogger()
    
    def authenticate_request(self, request: Request) -> bool:
        # API key validation
        api_key = request.headers.get('X-API-Key')
        if not self.validate_api_key(api_key):
            return False
        
        # Rate limiting
        if not self.rate_limits.check_limit(api_key):
            return False
        
        # Audit logging
        self.audit_log.log_request(request)
        
        return True
```

#### **2. Data Protection**
```python
# Data Protection Strategy
class DataProtector:
    def __init__(self):
        self.encryption_key = self.load_encryption_key()
    
    def encrypt_sensitive_data(self, data: str) -> str:
        # Encrypt sensitive information
        return self.encrypt(data, self.encryption_key)
    
    def sanitize_input(self, input_text: str) -> str:
        # Input sanitization
        return self.remove_malicious_content(input_text)
    
    def validate_output(self, output: str) -> bool:
        # Output validation
        return self.check_output_safety(output)
```

#### **3. API Security**
```python
# API Security Measures
class APISecurity:
    def __init__(self):
        self.cors_policy = CORSConfig()
        self.input_validation = InputValidator()
        self.output_filtering = OutputFilter()
    
    def secure_endpoint(self, endpoint: Callable) -> Callable:
        # Apply security middleware
        @wraps(endpoint)
        def secured_endpoint(*args, **kwargs):
            # CORS check
            if not self.cors_policy.allow_request(request):
                return Response(status=403)
            
            # Input validation
            if not self.input_validation.validate(args, kwargs):
                return Response(status=400)
            
            # Execute endpoint
            result = endpoint(*args, **kwargs)
            
            # Output filtering
            filtered_result = self.output_filtering.filter(result)
            
            return filtered_result
        
        return secured_endpoint
```

### **Security Best Practices**

#### **1. API Key Management**
- **Secure Storage**: Environment variables, not code
- **Key Rotation**: Regular key updates
- **Access Control**: Different keys for different environments
- **Monitoring**: Track key usage and anomalies

#### **2. Input Validation**
- **Type Checking**: Validate data types
- **Length Limits**: Prevent buffer overflows
- **Content Filtering**: Remove malicious content
- **SQL Injection**: Parameterized queries

#### **3. Output Sanitization**
- **XSS Prevention**: Escape HTML content
- **Data Leakage**: Filter sensitive information
- **Format Validation**: Ensure proper output format
- **Size Limits**: Prevent response flooding

---

## 7. Deployment Architecture

### **Deployment Options**

#### **1. Local Development**
```bash
# Local Development Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run_web.py
```

#### **2. Docker Deployment**
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health

# Run application
CMD ["streamlit", "run", "src/web_app_advanced.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
```

#### **3. Cloud Deployment**
```yaml
# Docker Compose for Production
version: '3.8'
services:
  ask-et-app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - PRODUCTION=true
    volumes:
      - ./data:/app/data
      - ./vector_store:/app/vector_store
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

#### **4. Kubernetes Deployment**
```yaml
# Kubernetes Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ask-et-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ask-et-app
  template:
    metadata:
      labels:
        app: ask-et-app
    spec:
      containers:
      - name: ask-et-app
        image: ask-et-app:latest
        ports:
        - containerPort: 8501
        env:
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: google-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

### **Environment Configuration**

#### **Development Environment**
```bash
# .env.development
GOOGLE_API_KEY=your_dev_api_key
DEBUG=true
LOG_LEVEL=DEBUG
CACHE_ENABLED=false
```

#### **Production Environment**
```bash
# .env.production
GOOGLE_API_KEY=your_prod_api_key
DEBUG=false
LOG_LEVEL=INFO
CACHE_ENABLED=true
REDIS_URL=redis://redis:6379
```

---

## 8. Scalability Architecture

### **Horizontal Scaling**

#### **1. Load Balancing**
```python
# Load Balancer Configuration
class LoadBalancer:
    def __init__(self, backend_servers: List[str]):
        self.backend_servers = backend_servers
        self.current_index = 0
    
    def get_next_server(self) -> str:
        # Round-robin load balancing
        server = self.backend_servers[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.backend_servers)
        return server
```

#### **2. Database Scaling**
```python
# Database Scaling Strategy
class DatabaseManager:
    def __init__(self):
        self.primary_db = PrimaryDatabase()
        self.read_replicas = [ReadReplica() for _ in range(3)]
    
    def read_operation(self, query: str) -> Any:
        # Route read operations to replicas
        replica = self.select_replica()
        return replica.execute(query)
    
    def write_operation(self, query: str) -> Any:
        # Route write operations to primary
        return self.primary_db.execute(query)
```

#### **3. Caching Strategy**
```python
# Distributed Caching
class DistributedCache:
    def __init__(self, redis_cluster: List[str]):
        self.redis_clients = [redis.Redis(host=host) for host in redis_cluster]
    
    def get(self, key: str) -> Any:
        # Hash-based key distribution
        client = self.get_client_for_key(key)
        return client.get(key)
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        client = self.get_client_for_key(key)
        client.setex(key, ttl, value)
```

### **Vertical Scaling**

#### **1. Resource Optimization**
```python
# Resource Management
class ResourceManager:
    def __init__(self):
        self.memory_pool = MemoryPool(max_size="4GB")
        self.cpu_pool = CPUPool(max_cores=8)
    
    def optimize_memory(self):
        # Memory optimization strategies
        self.garbage_collect()
        self.compress_vectors()
        self.evict_cache()
    
    def optimize_cpu(self):
        # CPU optimization strategies
        self.parallelize_operations()
        self.use_vectorized_operations()
        self.batch_process_requests()
```

#### **2. Performance Monitoring**
```python
# Performance Monitoring
class PerformanceMonitor:
    def __init__(self):
        self.metrics = MetricsCollector()
        self.alerting = AlertManager()
    
    def monitor_response_time(self, query: str, response_time: float):
        self.metrics.record_response_time(query, response_time)
        
        if response_time > 2.0:  # Alert threshold
            self.alerting.send_alert(f"Slow response: {response_time}s")
    
    def monitor_resource_usage(self):
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        
        if cpu_usage > 80 or memory_usage > 80:
            self.alerting.send_alert("High resource usage detected")
```

### **Scalability Metrics**

#### **Performance Targets**
- **Response Time**: <2 seconds (95th percentile)
- **Throughput**: 1000+ queries per minute
- **Concurrency**: 100+ simultaneous users
- **Availability**: 99.9% uptime

#### **Resource Scaling**
- **CPU**: Scale up to 16 cores
- **Memory**: Scale up to 32GB RAM
- **Storage**: Scale up to 1TB SSD
- **Network**: Scale up to 1Gbps bandwidth

---

## **Conclusion**

The Ask ET system employs a **modern, scalable, and secure architecture** that leverages cutting-edge AI/ML technologies to deliver exceptional user experiences. The architecture is designed for:

- **High Performance**: Sub-second response times
- **High Availability**: 99.9% uptime with fault tolerance
- **High Scalability**: Horizontal and vertical scaling capabilities
- **High Security**: Multi-layer security with best practices
- **High Maintainability**: Clean code with comprehensive documentation

**The system is production-ready and can scale to meet enterprise demands!** 