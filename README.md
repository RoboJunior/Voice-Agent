# RAG Voice Bot

RAG Voice Bot is an **end-to-end voice-based Retrieval-Augmented Generation (RAG) assistant**.  
It enables users to ask questions through speech and receive responses as natural speech, powered by **Qdrant**, **LangChain**, **Deepgram**, **Google Gemini**, and **ElevenLabs**.  

The system is designed with a **modular ingestion pipeline**, an **MCP server for retrieval coordination**, and a **voice agent** that handles user interaction seamlessly.  

---

## Features

- **Voice Input → Text**: Speech converted to text using **Deepgram**.  
- **Document & URL Ingestion**:  
  - URLs crawled using **Crawl4AI**.  
  - PDFs processed with **PyPDF**, extracting text **page by page**.  
- **Chunking**: Smart semantic chunking via **LangChain Semantic-Chunker**, backed by **BAAI/bge-small-en** embeddings.  
- **Knowledge Base**: Stored in **Qdrant VectorDB** (deployed on GCP free instance).  
- **Similarity Search**: Qdrant queried via the ingestion service (`/search` API).  
- **LLM Agent**: Powered by **Google Gemini 2.5 Flash** (via `google-adk LLMAgent`).  
- **Text → Voice Output**: Responses synthesized with **ElevenLabs TTS**.  
- **Async Messaging Pipeline**:  
  - `asyncio` Message Queue for task orchestration.  
  - Responses streamed via **SSE** (currently Postman used for testing).  
- **Modular Ingestion Sources**: Implemented using **Factory Design Pattern** for easy extensibility.  
- **Configuration**: Managed with **Pydantic Settings** + **LRU Cache** (optimized `.env` loading).  
- **Monitoring & Tracing**: Integrated with **Opik** for agent observability.  

---

## 🏗️ Architecture Overview

```mermaid
flowchart TD
    subgraph InputModule["Input Processing Module"]
        UserInput["User<br>Speech Input"]
        STT["Deepgram<br>STT Service"]
        Queue["Asyncio<br>Message Queue"]
    end
    
    subgraph FactoryPattern["Factory Design Pattern"]
        URLSource["URL Source"]
        PDFSource["PDF Source"]
        NewSource["Future Sources<br>(Modular Design)"]
        FactoryInterface["Ingestion<br>Factory Interface"]
        Crawl4AI["Crawl4AI<br>Web Crawler"]
        PyPDF["PyPDF<br>Text Extractor<br>(Page-by-Page)"]
    end
    
    subgraph ProcessingLayer["Text Processing Layer"]
        SemanticChunker["Semantic<br>Text Chunker"]
        Embeddings["Text<br>Embeddings"]
        VectorStore["Vector<br>Database<br>(Qdrant)"]
    end
    
    subgraph MCPLayer["MCP Server Layer"]
        MCPServer["MCP Server"]
        SearchRoute["Ingestion Service<br>/search Route"]
    end
    
    subgraph KnowledgeRetrieval["Knowledge Retrieval System"]
        SimilarityResults["Similar Vectors<br>BAAI/bge-small-en<br>Vector Search"]
    end
    
    subgraph AgentModule["Agent Processing Module"]
        LLMAgent["Google ADK<br>LLM Agent<br>(Gemini 2.5 Flash)"]
    end
    
    subgraph MonitoringModule["Agent Monitoring"]
        OpikTracing["Opik<br>Agent Monitoring"]
    end
    
    subgraph OutputModule["Output Delivery Module"]
        SSE["Server-Sent Events"]
        PostmanClient["Postman /<br>Client Application"]
        TTS["ElevenLabs<br>TTS Service"]
        UserOutput["User<br>Audio Response"]
    end
    
    subgraph CloudInfra["Cloud Infrastructure"]
        GCPCloud["Google Cloud Platform<br>(Free Instance)"]
    end
    
    %% Main Flow Connections
    UserInput --> STT
    STT --> Queue
    
    %% Data Ingestion Flow
    URLSource --> Crawl4AI
    PDFSource --> PyPDF
    NewSource -.-> FactoryInterface
    Crawl4AI --> SemanticChunker
    PyPDF --> SemanticChunker
    FactoryInterface -.-> SemanticChunker
    
    %% Processing Flow
    SemanticChunker --> Embeddings
    Embeddings --> VectorStore
    
    %% Agent Processing Flow
    STT --> LLMAgent
    LLMAgent <--> MCPServer
    MCPServer --> SearchRoute
    SearchRoute --> VectorStore
    VectorStore --> SimilarityResults
    SimilarityResults --> SearchRoute
    SearchRoute --> MCPServer
    MCPServer --> LLMAgent
    
    %% Output Flow
    LLMAgent --> Queue
    Queue --> SSE
    SSE --> PostmanClient
    LLMAgent --> TTS
    TTS --> UserOutput
    
    %% Monitoring
    LLMAgent -.-> OpikTracing
    
    %% Cloud Connection
    VectorStore -.-> GCPCloud
    
    %% Styles
    classDef moduleStyle fill:#f8f9fa,stroke:#495057,stroke-width:2px,color:#000
    classDef serviceStyle fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    classDef databaseStyle fill:#fff8e1,stroke:#f57c00,stroke-width:2px,color:#000
    classDef userStyle fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000
    classDef monitoringStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef factoryStyle fill:#e0f2f1,stroke:#00796b,stroke-width:2px,color:#000
    classDef cloudStyle fill:#e1f5fe,stroke:#0288d1,stroke-width:2px,color:#000
    
    %% Apply styles
    UserInput:::userStyle
    UserOutput:::userStyle
    PostmanClient:::userStyle
    
    STT:::serviceStyle
    Crawl4AI:::serviceStyle
    PyPDF:::serviceStyle
    SemanticChunker:::serviceStyle
    Embeddings:::serviceStyle
    LLMAgent:::serviceStyle
    MCPServer:::serviceStyle
    SearchRoute:::serviceStyle
    SSE:::serviceStyle
    TTS:::serviceStyle
    Queue:::serviceStyle
    
    VectorStore:::databaseStyle
    SimilarityResults:::databaseStyle
    
    OpikTracing:::monitoringStyle
    
    NewSource:::factoryStyle
    FactoryInterface:::factoryStyle
    
    GCPCloud:::cloudStyle
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Poetry
- API keys for: Deepgram, Google API Key, ElevenLabs

### Installation

```bash
git clone https://github.com/RoboJunior/Voice-Agent.git

cd Voice-Agent/

# Install ingestion
cd ingestion/
poetry install

# Intall mcp server
cd tools/
poetry install

# Install voice agent
cd agents/
poetry install

```

### Start Services
```bash
# To Create a new session session in qdrant
poetry run create_new_collection "<new-collection-name>"

# Start the voice agent
cd agents/
poetry run voice_agent

# Start the MCP server
cd tools/
poetry run mcp_server

# Start the ingestion service
cd ingestion/
poetry run ingestion_service
```

## 🔌 API Endpoints

### Ingestion Service
```http
POST v1/ingest/data
GET v1/ingest/search
```

### MCP Server
```http
POST /mcp
```

## 🔗 Technology Stack

| Component | Technology |
|-----------|------------|
| **Web Crawling** | Crawl4AI |
| **PDF Processing** | PyPDF |
| **Text Chunking** | LangChain Semantic Chunker |
| **Embeddings** | BAAI/bge-small-en |
| **Vector Database** | Qdrant (GCP) |
| **Speech-to-Text** | Deepgram |
| **Large Language Model** | Gemini 2.5 Flash |
| **Agent Framework** | Google ADK |
| **Text-to-Speech** | ElevenLabs |
| **Protocol** | MCP (Model Context Protocol) |
| **Monitoring** | OpIK |
| **Streaming** | Server-Sent Events (SSE) |

## 🎥 Demo Video
Here is the Demo of the Voice-Agent along with Opik Observability  

📽️ [Watch Demo Video](https://drive.google.com/file/d/1ukTjDP07IuNwVkEPbddYjhAlD033SUaU/view?usp=sharing)
