import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import faiss
import numpy as np

logger = logging.getLogger(__name__)

# OpenAI client (lazy initialization)
_openai_client = None

def get_openai_client():
    """Get or initialize OpenAI client."""
    global _openai_client
    if _openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                from openai import OpenAI
                _openai_client = OpenAI(api_key=api_key)
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                _openai_client = False  # Mark as unavailable
        else:
            logger.warning("OPENAI_API_KEY not set, will use extractive answers")
            _openai_client = False
    return _openai_client if _openai_client is not False else None

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
BANK_DOCS_DIR = DATA_DIR / "bank_docs"
RAG_INDEX_DIR = DATA_DIR / "rag_index"

# Ensure directories exist
RAG_INDEX_DIR.mkdir(parents=True, exist_ok=True)

# Global variables
_embedding_model = None
_vector_index = None
_chunk_metadata = []  # List of {source, page, chunk_id, text}


def get_embedding_model():
    """Get or initialize the embedding model."""
    global _embedding_model
    if _embedding_model is None:
        logger.info("Loading sentence-transformers model...")
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedding_model


def load_index():
    """Load the FAISS index and metadata from disk."""
    global _vector_index, _chunk_metadata
    
    index_path = RAG_INDEX_DIR / "index.faiss"
    metadata_path = RAG_INDEX_DIR / "metadata.json"
    
    if index_path.exists() and metadata_path.exists():
        try:
            # Convert to absolute path string for Windows compatibility
            # Use resolve() to handle any symlinks or relative paths
            index_path_str = str(index_path.resolve())
            metadata_path_str = str(metadata_path.resolve())
            
            # Check file size to ensure it's not corrupted
            if index_path.stat().st_size == 0:
                logger.warning("Index file is empty, will rebuild")
                return False
            
            _vector_index = faiss.read_index(index_path_str)
            with open(metadata_path_str, 'r', encoding='utf-8') as f:
                _chunk_metadata = json.load(f)
            logger.info(f"Loaded index with {len(_chunk_metadata)} chunks")
            return True
        except Exception as e:
            logger.error(f"Error loading index: {e}", exc_info=True)
            # If loading fails, try to delete corrupted index
            try:
                if index_path.exists():
                    index_path.unlink()
                if metadata_path.exists():
                    metadata_path.unlink()
                logger.info("Removed corrupted index files")
            except:
                pass
            return False
    return False


def save_index():
    """Save the FAISS index and metadata to disk."""
    global _vector_index, _chunk_metadata
    
    if _vector_index is None or not _chunk_metadata:
        logger.warning("No index to save")
        return
    
    try:
        index_path = RAG_INDEX_DIR / "index.faiss"
        metadata_path = RAG_INDEX_DIR / "metadata.json"
        
        # Convert to absolute path string for Windows compatibility
        index_path_str = str(index_path.absolute())
        faiss.write_index(_vector_index, index_path_str)
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(_chunk_metadata, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved index with {len(_chunk_metadata)} chunks")
    except Exception as e:
        logger.error(f"Error saving index: {e}", exc_info=True)


def extract_pdf_with_pages(pdf_path: Path) -> List[Dict[str, Any]]:
    """Extract text from PDF with page numbers."""
    try:
        # Convert to absolute path string for Windows compatibility
        pdf_path_str = str(pdf_path.absolute())
        loader = PyPDFLoader(pdf_path_str)
        pages = loader.load()
        
        documents = []
        for i, page in enumerate(pages):
            documents.append({
                "page_number": i + 1,  # 1-indexed
                "text": page.page_content,
                "source": pdf_path.name
            })
        return documents
    except Exception as e:
        logger.error(f"Error extracting PDF {pdf_path}: {e}")
        # Fallback to pdfplumber if PyPDFLoader fails
        try:
            import pdfplumber
            documents = []
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        documents.append({
                            "page_number": i + 1,
                            "text": text,
                            "source": pdf_path.name
                        })
            return documents
        except Exception as e2:
            logger.error(f"Error with pdfplumber fallback: {e2}")
            return []


def build_index():
    """Build RAG index from PDFs in bank_docs directory."""
    global _vector_index, _chunk_metadata
    
    logger.info("Building RAG index from bank_docs...")
    
    if not BANK_DOCS_DIR.exists():
        logger.warning(f"Bank docs directory not found: {BANK_DOCS_DIR}")
        return {"status": "error", "message": "Bank docs directory not found"}
    
    # Find all PDF files
    pdf_files = list(BANK_DOCS_DIR.glob("*.pdf"))
    if not pdf_files:
        logger.warning("No PDF files found in bank_docs")
        return {"status": "error", "message": "No PDF files found"}
    
    logger.info(f"Found {len(pdf_files)} PDF files")
    
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    # Extract and chunk all documents
    all_chunks = []
    model = get_embedding_model()
    
    for pdf_path in pdf_files:
        logger.info(f"Processing {pdf_path.name}...")
        pages = extract_pdf_with_pages(pdf_path)
        
        for page_doc in pages:
            # Split page text into chunks
            chunks = text_splitter.split_text(page_doc["text"])
            
            for chunk_idx, chunk_text in enumerate(chunks):
                if len(chunk_text.strip()) < 50:  # Skip very short chunks
                    continue
                
                chunk_id = f"{pdf_path.stem}_page{page_doc['page_number']}_chunk{chunk_idx}"
                all_chunks.append({
                    "chunk_id": chunk_id,
                    "source": page_doc["source"],
                    "page": page_doc["page_number"],
                    "text": chunk_text,
                    "snippet": chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text
                })
    
    if not all_chunks:
        logger.warning("No chunks created from PDFs")
        return {"status": "error", "message": "No chunks created"}
    
    logger.info(f"Created {len(all_chunks)} chunks, generating embeddings...")
    
    # Generate embeddings
    texts = [chunk["text"] for chunk in all_chunks]
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
    
    # Create FAISS index
    dimension = embeddings.shape[1]
    _vector_index = faiss.IndexFlatL2(dimension)
    _vector_index.add(embeddings.astype('float32'))
    
    # Store metadata
    _chunk_metadata = all_chunks
    
    # Save to disk
    save_index()
    
    logger.info(f"Index built successfully with {len(all_chunks)} chunks from {len(pdf_files)} PDFs")
    
    return {
        "status": "success",
        "num_documents": len(pdf_files),
        "num_chunks": len(all_chunks)
    }


def query_rag(question: str, top_k: int = 10) -> Dict[str, Any]:
    """Query the RAG system and return answer with sources."""
    global _vector_index, _chunk_metadata
    
    if _vector_index is None or not _chunk_metadata:
        # Try to load index
        if not load_index():
            return {
                "answer": "No index found. Please reindex the documents first.",
                "sources": []
            }
    
    try:
        # Validate index state
        if _vector_index is None:
            return {
                "answer": "Index not loaded. Please reindex the documents.",
                "sources": []
            }
        
        if not _chunk_metadata:
            return {
                "answer": "No chunks in metadata. Please reindex the documents.",
                "sources": []
            }
        
        model = get_embedding_model()
        
        # Generate query embedding - enhance query for better results
        # For "what is X" questions, add synonyms and related terms
        enhanced_question = question
        question_lower = question.lower()
        
        # Enhance question for better matching
        if 'çfarë' in question_lower or 'what' in question_lower or 'ç\'është' in question_lower:
            # Add common terms that might help find definitions
            enhanced_question = f"{question} definition përkufizim explanation shpjegim"
        
        try:
            query_embedding = model.encode([enhanced_question], show_progress_bar=False)[0].astype('float32')
            query_embedding = query_embedding.reshape(1, -1)
        except Exception as e:
            logger.error(f"Error encoding query: {e}", exc_info=True)
            return {
                "answer": f"Error processing your question: {str(e)}",
                "sources": []
            }
        
        # Validate embedding dimensions
        if _vector_index.d != query_embedding.shape[1]:
            logger.error(f"Dimension mismatch: index={_vector_index.d}, query={query_embedding.shape[1]}")
            return {
                "answer": "Index dimension mismatch. Please reindex the documents.",
                "sources": []
            }
        
        # Search in FAISS index
        k = min(top_k, len(_chunk_metadata))
        if k <= 0:
            return {
                "answer": "No chunks available in the index.",
                "sources": []
            }
        
        try:
            distances, indices = _vector_index.search(query_embedding, k)
        except Exception as e:
            logger.error(f"Error searching FAISS index: {e}", exc_info=True)
            return {
                "answer": f"Error searching index: {str(e)}. Please try reindexing.",
                "sources": []
            }
        
        # Get relevant chunks and filter by relevance
        sources = []
        chunks_texts = []
        question_words = set(word.lower() for word in question.split() if len(word) > 2)
        
        for idx, (distance, chunk_idx) in enumerate(zip(distances[0], indices[0])):
            # Handle invalid indices
            if chunk_idx < 0 or chunk_idx >= len(_chunk_metadata):
                continue
            
            chunk = _chunk_metadata[int(chunk_idx)]
            chunk_text = chunk["text"].lower()
            
            # Calculate relevance score based on distance and keyword matching
            score = max(0, 1 - (distance / 10))  # Base score from embedding similarity
            
            # Boost score if chunk contains question keywords
            keyword_matches = sum(1 for word in question_words if word in chunk_text)
            if keyword_matches > 0:
                score += 0.1 * min(keyword_matches, 3)  # Boost up to 0.3
            
            # Boost score for definition-like content
            definition_keywords = ['përkufizim', 'definition', 'është', 'is', 'means', 'do të thotë', 'refers to']
            if any(keyword in chunk_text for keyword in definition_keywords):
                score += 0.2
            
            sources.append({
                "source": chunk["source"],
                "page": chunk["page"],
                "snippet": chunk["snippet"],
                "score": round(min(score, 1.0), 3)  # Cap at 1.0
            })
            
            chunks_texts.append(chunk["text"])
        
        # Sort by score and take top chunks
        if sources and chunks_texts:
            combined = list(zip(sources, chunks_texts))
            combined.sort(key=lambda x: x[0]["score"], reverse=True)
            sources, chunks_texts = zip(*combined) if combined else ([], [])
            sources = list(sources[:8])  # Take top 8 most relevant
            chunks_texts = list(chunks_texts[:8])
        
        # Generate answer using OpenAI if available, otherwise use extractive method
        if chunks_texts:
            answer = generate_answer_with_openai(question, chunks_texts, sources)
        else:
            answer = "I couldn't find relevant information in the documents for your question."
        
        return {
            "answer": answer,
            "sources": sources
        }
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error querying RAG: {e}\n{error_details}")
        return {
            "answer": f"Error processing your question: {str(e)}. Please try again or reindex the documents.",
            "sources": []
        }


def generate_answer_with_openai(question: str, context_chunks: List[str], sources: List[Dict[str, Any]]) -> str:
    """Generate an intelligent answer using OpenAI based on the retrieved context."""
    client = get_openai_client()
    
    # If OpenAI is not available, fall back to improved extractive method
    if not client:
        logger.info("OpenAI not available, using improved extractive answer")
        return generate_extractive_answer(question, context_chunks, sources)
    
    try:
        # Combine context chunks with source information
        context_parts = []
        for i, (chunk, source) in enumerate(zip(context_chunks[:5], sources[:5]), 1):
            source_name = source.get("source", "Document")
            page = source.get("page", "?")
            context_parts.append(f"[Source {i}: {source_name}, Page {page}]\n{chunk}")
        
        context_text = "\n\n".join(context_parts)
        
        # Create a comprehensive prompt
        system_prompt = """You are a helpful banking document assistant. Your role is to answer questions based EXCLUSIVELY on the provided context from banking documents (PDFs about AML policies, KYC procedures, transaction monitoring, etc.).

IMPORTANT INSTRUCTIONS:
1. Answer the question based ONLY on the information provided in the context below
2. Provide a COMPREHENSIVE and DETAILED explanation - do not just repeat the question or give a one-line answer
3. If asked "what is X", explain what X is, its purpose, key characteristics, and relevant details from the documents
4. If the context contains relevant information, provide a clear, thorough answer with multiple sentences
5. If the context doesn't contain enough information to fully answer, provide the best answer you can based on what is available
6. DO NOT ask clarifying questions - always provide the best answer possible with the available information
7. Write in a natural, conversational style like ChatGPT - be informative and helpful
8. Be specific and include details from the documents
9. Structure your answer logically: start with a definition/overview, then add details
10. If multiple sources are mentioned, you can reference them naturally in your answer

Answer in the same language as the question (Albanian, English, etc.)."""

        user_prompt = f"""Context from banking documents:

{context_text}

Question: {question}

Please provide a comprehensive, detailed answer based on the context above. 
- If the question asks "what is X", explain what X is, its purpose, and key details
- Provide a thorough explanation with multiple sentences
- Use information from the context to give a complete answer
- Answer naturally and conversationally, without asking clarifying questions
- Make sure your answer is informative and helpful, not just a brief mention."""

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using gpt-4o-mini for cost-effectiveness, can be changed to gpt-4 or gpt-3.5-turbo
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content.strip()
        logger.info("Generated answer using OpenAI")
        return answer
        
    except Exception as e:
        logger.error(f"Error generating answer with OpenAI: {e}", exc_info=True)
        # Fallback to improved extractive method
        return generate_extractive_answer(question, context_chunks, sources)


def generate_extractive_answer(question: str, context_chunks: List[str], sources: List[Dict[str, Any]]) -> str:
    """Generate an answer by intelligently extracting and combining relevant information from chunks."""
    if not context_chunks:
        return "Nuk gjetëm informacion të mjaftueshëm në dokumentet për këtë pyetje."
    
    # Clean and filter chunks
    relevant_chunks = []
    question_lower = question.lower()
    question_words = set(word.lower() for word in question.split() if len(word) > 2)
    
    # Find the most relevant sentences from chunks
    relevant_sentences = []
    
    for chunk in context_chunks[:5]:  # Use top 5 chunks
        if not chunk or len(chunk.strip()) < 20:
            continue
        
        # Split into sentences
        sentences = chunk.replace('\n', ' ').split('. ')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 30:  # Skip very short sentences
                continue
            
            sentence_lower = sentence.lower()
            # Check if sentence contains question words or is relevant
            sentence_words = set(word.lower() for word in sentence.split() if len(word) > 2)
            
            # Calculate relevance: count matching words
            matches = len(question_words.intersection(sentence_words))
            
            # Also check for key terms from question
            if any(word in sentence_lower for word in question_words if len(word) > 3):
                matches += 2
            
            if matches > 0 or any(keyword in sentence_lower for keyword in ['është', 'is', 'are', 'definition', 'përkufizim', 'do të thotë', 'means']):
                relevant_sentences.append((sentence, matches))
    
    # Sort by relevance
    relevant_sentences.sort(key=lambda x: x[1], reverse=True)
    
    # Build answer
    if relevant_sentences:
        # Take top relevant sentences
        top_sentences = [s[0] for s in relevant_sentences[:5]]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_sentences = []
        for sent in top_sentences:
            sent_key = sent.lower()[:50]  # Use first 50 chars as key
            if sent_key not in seen:
                seen.add(sent_key)
                unique_sentences.append(sent)
        
        # Combine into answer
        answer = ". ".join(unique_sentences)
        if not answer.endswith('.'):
            answer += "."
        
        # Limit length
        if len(answer) > 800:
            answer = answer[:800] + "..."
        
        return answer
    else:
        # Fallback: use first chunk intelligently
        first_chunk = context_chunks[0]
        # Try to extract first few sentences
        sentences = first_chunk.replace('\n', ' ').split('. ')
        relevant = [s.strip() for s in sentences[:3] if len(s.strip()) > 30]
        
        if relevant:
            answer = ". ".join(relevant)
            if not answer.endswith('.'):
                answer += "."
            return answer[:600] + "..." if len(answer) > 600 else answer
        else:
            # Last resort: return first part of chunk
            return first_chunk[:500] + "..." if len(first_chunk) > 500 else first_chunk


def get_index_status() -> Dict[str, Any]:
    """Get status of the RAG index."""
    global _vector_index, _chunk_metadata
    
    if _vector_index is None:
        if not load_index():
            return {
                "indexed": False,
                "num_documents": 0,
                "num_chunks": 0
            }
    
    # Count unique documents
    unique_docs = set(chunk["source"] for chunk in _chunk_metadata)
    
    return {
        "indexed": True,
        "num_documents": len(unique_docs),
        "num_chunks": len(_chunk_metadata)
    }
