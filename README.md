<<<<<<< HEAD
# ML Project - Risk & Compliance Management System

A complete full-stack monorepo application for document analysis, compliance checking, risk scoring, and anomaly detection.

## Project Structure

```
ML_Project/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py       # FastAPI application entry point
│   │   ├── models.py     # Pydantic models
│   │   ├── routers/      # API route handlers
│   │   └── services/     # Business logic services
│   ├── requirements.txt  # Python dependencies
│   ├── start.bat         # Windows start script
│   └── start.sh          # Linux/Mac start script
├── frontend/             # React + TypeScript frontend
│   ├── src/
│   │   ├── pages/        # React page components
│   │   ├── components/   # UI components (shadcn/ui)
│   │   └── lib/          # Utilities and API client
│   ├── package.json      # Node.js dependencies
│   └── vite.config.ts    # Vite configuration
└── data/                 # Data storage
    ├── customers.csv     # Sample customer data
    ├── transactions.csv  # Sample transaction data
    ├── regulations/      # Regulation markdown files
    ├── uploads/          # Uploaded documents
    └── reports/          # Generated reports
```

## Features

- **Document Upload & Processing**: Upload PDF, DOCX, TXT, MD, XLSX files with text extraction
- **Intelligent Chat Assistant**: Ask questions about banking documents (PDFs in `data/bank_docs/`) - powered by OpenAI GPT-4o-mini with RAG
- **RAG (Retrieval Augmented Generation)**: Vector store with sentence-transformers embeddings and OpenAI for answer generation
- **Compliance Checking**: Compare documents against regulations from `data/regulations/*.md`
- **Risk Scoring**: Calculate risk scores (0-100) based on violations and suspicious terms
- **Anomaly Detection**: Detect outliers in transactions using z-score and IQR methods
- **Alerts**: Automatic alerts for high-risk documents and anomalies
- **Reports**: Generate PDF and Excel reports

## Prerequisites

- Python 3.9+ (tested on 3.12)
- Node.js 18+ and npm
- (Optional) Tesseract OCR for PDF OCR support

## Setup Instructions for Windows

### Quick Start (Recommended)

Start both backend and frontend with one command:

```powershell
# From the project root directory
.\start.bat
```

Or using PowerShell:

```powershell
.\start.ps1
```

This will open two separate terminal windows:

- **Backend** running on `http://127.0.0.1:8000`
- **Frontend** running on `http://localhost:3000`

### Manual Setup (Alternative)

If you prefer to start servers manually:

#### 1. Backend Setup

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
.\start.bat
```

The backend will run on `http://127.0.0.1:8000`

#### 2. Frontend Setup

Open a new terminal:

```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will run on `http://localhost:3000`

### 3. Verify Installation

1. Open `http://localhost:3000` in your browser
2. Check the Dashboard page - it should show initial statistics
3. Try uploading a document from the Documents page
4. Check the API health endpoint: `http://127.0.0.1:8000/health`

## API Endpoints

- `GET /health` - Health check
- `POST /api/documents/upload` - Upload and process document
- `GET /api/documents` - List all documents
- `GET /api/documents/{document_id}` - Get document details
- `GET /api/rag/query?q=...` - Query RAG system
- `POST /api/chat/ask` - Ask questions about banking documents (Chat feature)
- `POST /api/chat/reindex` - Rebuild PDF index from `data/bank_docs/`
- `GET /api/chat/status` - Get chat index status
- `POST /api/compliance/check/{document_id}` - Check compliance
- `GET /api/risk/scores` - Get all risk scores
- `GET /api/risk/dashboard` - Get risk dashboard
- `GET /api/anomalies` - Get detected anomalies
- `GET /api/alerts` - Get all alerts
- `POST /api/reports/generate` - Generate PDF and Excel reports

## Configuration

### OpenAI API Key (Required for Chat Feature)

The chat feature uses **OpenAI GPT-4o-mini** to generate intelligent, conversational answers based on your PDF documents. This is **highly recommended** for the best chat experience.

1. Get an OpenAI API key from https://platform.openai.com/
2. Set environment variable:

   ```powershell
   $env:OPENAI_API_KEY="your-api-key-here"
   ```
3. Restart the backend server

**Note**: Without the API key, the chat will still work but will use simple extractive answers (text concatenation) which are less natural and conversational.

### OpenAI Embeddings (Optional)

To use OpenAI embeddings instead of sentence-transformers for document indexing:

1. Set environment variable (same as above):

   ```powershell
   $env:OPENAI_API_KEY="your-api-key-here"
   ```
2. Restart the backend server

### OCR Support (Optional)

For PDF OCR support:

1. Install Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
2. Install pdf2image:
   ```powershell
   pip install pdf2image
   ```
3. Ensure Tesseract is in your PATH

## Sample Data

The project includes sample data:

- `data/customers.csv` - Customer information
- `data/transactions.csv` - Transaction data for anomaly detection
- `data/regulations/*.md` - Sample regulation files

## Troubleshooting

### Backend won't start

- Ensure Python 3.9+ is installed: `python --version`
- Check that all dependencies are installed: `pip list`
- Verify port 8000 is not in use

### Frontend won't start

- Ensure Node.js 18+ is installed: `node --version`
- Clear node_modules and reinstall: `rm -r node_modules && npm install`
- Check that port 3000 is not in use

### CORS errors

- Ensure backend is running on `http://127.0.0.1:8000`
- Check CORS settings in `backend/app/main.py`

### Document upload fails

- Check file size limits
- Verify file type is supported (PDF, DOCX, TXT, MD, XLSX)
- Check backend logs for errors

## Development

### Backend Development

- Backend uses FastAPI with auto-reload enabled
- Logs are printed to console
- API documentation available at `http://127.0.0.1:8000/docs`

### Frontend Development

- Frontend uses Vite with hot module replacement
- TypeScript for type safety
- Tailwind CSS for styling
- shadcn/ui components for UI
=======
# ml-risk-compliance
>>>>>>> 4f6403bb4f5d9827863465685fe010bbbd153f6d
