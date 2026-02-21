# Arkitektura e Projektit ML - Risk & Compliance Management System

## Diagrami i Arkitekturës

```mermaid
graph TB
    subgraph "Frontend - React + TypeScript"
        UI[Interfaça e Përdoruesit]
        Pages[Faqet:<br/>Dashboard, Documents,<br/>Compliance, Risk,<br/>Anomalies, Reports,<br/>Alerts, Chat]
        API_Client[API Client]
    end

    subgraph "Backend - FastAPI"
        subgraph "Routers"
            Health[Health Router]
            Docs[Documents Router]
            Chat[Chat Router]
            RAG[RAG Router]
            Compliance[Compliance Router]
            Risk[Risk Router]
            Anomalies[Anomalies Router]
            Reports[Reports Router]
            Alerts[Alerts Router]
        end

        subgraph "Services"
            DocService[Document Service]
            ChatService[PDF RAG Service]
            RAGService[RAG Service]
            ComplianceService[Compliance Service]
            RiskService[Risk Service]
            AnomalyService[Anomaly Service]
            ReportService[Report Service]
            AlertService[Alert Service]
        end

        subgraph "AI & ML Components"
            OpenAI[OpenAI GPT-4o-mini<br/>Chat Generation]
            Embeddings[Sentence Transformers<br/>Embeddings]
            FAISS[FAISS Vector Index]
        end
    end

    subgraph "Storage"
        PDFs[PDF Files<br/>bank_docs/]
        Uploads[Uploaded Documents<br/>data/uploads/]
        Index[RAG Index<br/>data/rag_index/]
        Reports_Storage[Generated Reports<br/>data/reports/]
        Regulations[Regulations<br/>data/regulations/]
    end

    subgraph "External Services"
        OpenAI_API[OpenAI API]
    end

    %% Frontend connections
    UI --> Pages
    Pages --> API_Client
    API_Client -->|HTTP/REST| Health
    API_Client -->|HTTP/REST| Docs
    API_Client -->|HTTP/REST| Chat
    API_Client -->|HTTP/REST| Compliance
    API_Client -->|HTTP/REST| Risk
    API_Client -->|HTTP/REST| Anomalies
    API_Client -->|HTTP/REST| Reports
    API_Client -->|HTTP/REST| Alerts

    %% Router to Service connections
    Docs --> DocService
    Chat --> ChatService
    RAG --> RAGService
    Compliance --> ComplianceService
    Risk --> RiskService
    Anomalies --> AnomalyService
    Reports --> ReportService
    Alerts --> AlertService

    %% Service to Storage connections
    DocService --> Uploads
    ChatService --> PDFs
    ChatService --> Index
    RAGService --> Index
    ComplianceService --> Regulations
    ComplianceService --> Uploads
    RiskService --> Uploads
    AnomalyService --> Uploads
    ReportService --> Reports_Storage

    %% AI/ML connections
    ChatService --> Embeddings
    ChatService --> FAISS
    ChatService --> OpenAI
    RAGService --> Embeddings
    RAGService --> FAISS
    OpenAI --> OpenAI_API

    %% Index building
    PDFs -->|Indexing| FAISS
    Uploads -->|Indexing| FAISS

    style UI fill:#3b82f6,color:#fff
    style Pages fill:#6366f1,color:#fff
    style OpenAI fill:#10b981,color:#fff
    style FAISS fill:#f59e0b,color:#fff
    style PDFs fill:#8b5cf6,color:#fff
```

## Rrjedha e të Dhënave - Chat me RAG

```mermaid
sequenceDiagram
    participant User as Përdoruesi
    participant Frontend as Frontend
    participant ChatRouter as Chat Router
    participant RAGService as PDF RAG Service
    participant FAISS as FAISS Index
    participant Embeddings as Embeddings Model
    participant OpenAI as OpenAI API

    User->>Frontend: Bën pyetje
    Frontend->>ChatRouter: POST /api/chat/ask
    ChatRouter->>RAGService: query_rag(question)
    
    RAGService->>Embeddings: Generate query embedding
    Embeddings-->>RAGService: Query vector
    
    RAGService->>FAISS: Search similar chunks
    FAISS-->>RAGService: Top K chunks + sources
    
    RAGService->>OpenAI: Generate answer with context
    Note over OpenAI: GPT-4o-mini<br/>Uses context from PDFs
    OpenAI-->>RAGService: Generated answer
    
    RAGService-->>ChatRouter: Answer + Sources
    ChatRouter-->>Frontend: JSON Response
    Frontend-->>User: Shfaq përgjigjen
```

## Rrjedha e të Dhënave - Dokument Upload & Processing

```mermaid
flowchart TD
    Start([Përdoruesi ngarkon dokument]) --> Upload[Upload Document]
    Upload --> Extract[Extract Text]
    Extract --> Analyze{Type of Document?}
    
    Analyze -->|PDF/DOCX/TXT| TextAnalysis[Text Analysis]
    Analyze -->|CSV| CSVAnalysis[CSV Analysis]
    Analyze -->|XLSX| ExcelAnalysis[Excel Analysis]
    
    TextAnalysis --> AnomalyCheck[Document Anomaly Detection]
    CSVAnalysis --> CSVAnomalyCheck[CSV Anomaly Detection]
    ExcelAnalysis --> AnomalyCheck
    
    AnomalyCheck --> IndexRAG[Index in RAG]
    CSVAnomalyCheck --> IndexRAG
    
    IndexRAG --> Store[Store in Uploads]
    Store --> Response[Return Document ID]
    Response --> End([Dokumenti është gati])
```

## Komponentët e Sistemit

```mermaid
mindmap
  root((ML Project))
    Frontend
      React + TypeScript
      Vite
      Tailwind CSS
      shadcn/ui
      Pages
        Dashboard
        Documents
        Compliance
        Risk
        Anomalies
        Reports
        Alerts
        Chat
    Backend
      FastAPI
      Python 3.12
      Routers
        Health
        Documents
        Chat
        RAG
        Compliance
        Risk
        Anomalies
        Reports
        Alerts
      Services
        Document Service
        PDF RAG Service
        RAG Service
        Compliance Service
        Risk Service
        Anomaly Service
        Report Service
        Alert Service
    AI/ML
      OpenAI GPT-4o-mini
      Sentence Transformers
      FAISS Vector DB
      RAG Pipeline
      Embeddings
    Storage
      PDF Documents
      Uploaded Files
      RAG Index
      Generated Reports
      Regulations
```

## Rrjedha e Compliance Checking

```mermaid
graph LR
    A[Dokument Upload] --> B[Extract Text]
    B --> C[Load Regulations]
    C --> D[Compare Text with Regulations]
    D --> E{Shkelje të<br/>gjetura?}
    E -->|Po| F[Identify Violations]
    E -->|Jo| G[Dokument i Përputhshëm]
    F --> H[Calculate Risk Score]
    H --> I[Generate Alert]
    I --> J[Return Results]
    G --> J
```

## Teknologjitë e Përdorura

```mermaid
graph TB
    subgraph "Frontend Stack"
        React[React 18]
        TypeScript[TypeScript]
        Vite[Vite]
        Tailwind[Tailwind CSS]
    end

    subgraph "Backend Stack"
        FastAPI[FastAPI]
        Python[Python 3.12]
        Uvicorn[Uvicorn]
    end

    subgraph "AI/ML Stack"
        OpenAI_API[OpenAI API]
        SentenceTransformers[Sentence Transformers]
        FAISS[FAISS-CPU]
        LangChain[LangChain]
    end

    subgraph "Data Processing"
        PyPDF[PyPDF]
        PDFPlumber[PDFPlumber]
        Pandas[Pandas]
        NumPy[NumPy]
    end

    React --> FastAPI
    TypeScript --> React
    FastAPI --> OpenAI_API
    FastAPI --> SentenceTransformers
    FastAPI --> FAISS
    FastAPI --> PyPDF
    FastAPI --> Pandas
```
