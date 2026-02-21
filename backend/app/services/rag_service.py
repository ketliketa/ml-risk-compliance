import os
import logging
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)

# Global model instance
_model = None
_embeddings_cache: Dict[str, np.ndarray] = {}
_documents_cache: Dict[str, str] = {}
_document_sources: Dict[str, str] = {}  # Map chunk_id to document filename


def get_embedding_model():
    """Get or initialize the embedding model."""
    global _model
    if _model is None:
        try:
            use_openai = os.getenv("OPENAI_API_KEY")
            if use_openai:
                logger.info("Using OpenAI embeddings")
                # We'll use OpenAI client when needed
                _model = "openai"
            else:
                logger.info("Using sentence-transformers model")
                _model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


def get_embeddings_openai(text: str) -> List[float]:
    """Get embeddings using OpenAI."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"OpenAI embedding error: {e}")
        # Fallback to sentence-transformers
        model = SentenceTransformer('all-MiniLM-L6-v2')
        return model.encode(text).tolist()


def get_embeddings(text: str) -> np.ndarray:
    """Get embeddings for text."""
    model = get_embedding_model()
    
    if model == "openai":
        embedding = get_embeddings_openai(text)
        return np.array(embedding)
    else:
        return model.encode(text)


def index_document(document_id: str, text: str, chunk_size: int = 300, overlap: int = 50):
    """Index a document by chunking and creating embeddings with overlap."""
    if not text:
        return
    
    # Split text into paragraphs first (preserve structure)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    if not paragraphs:
        # Fallback to line-based splitting
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
    chunks = []
    chunk_metadata = []  # Store paragraph/line info for each chunk
    
    for para_idx, paragraph in enumerate(paragraphs):
        # If paragraph is small, add it as a chunk
        if len(paragraph) <= chunk_size:
            chunks.append(paragraph)
            chunk_metadata.append({
                "paragraph": para_idx + 1,
                "start_char": 0,
                "end_char": len(paragraph)
            })
        else:
            # Split large paragraph into sentences
            sentences = paragraph.replace('\n', ' ').split('. ')
            current_chunk = ""
            start_char = 0
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                # If adding this sentence would exceed chunk size, save current chunk
                if current_chunk and len(current_chunk) + len(sentence) > chunk_size:
                    chunks.append(current_chunk.strip())
                    chunk_metadata.append({
                        "paragraph": para_idx + 1,
                        "start_char": start_char,
                        "end_char": start_char + len(current_chunk)
                    })
                    # Start new chunk with overlap
                    words = current_chunk.split()
                    overlap_text = " ".join(words[-overlap:]) if len(words) > overlap else current_chunk
                    start_char = start_char + len(current_chunk) - len(overlap_text)
                    current_chunk = overlap_text + " " + sentence + ". "
                else:
                    if not current_chunk:
                        start_char = 0
                    current_chunk += sentence + ". "
            
            # Add remaining chunk
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
                chunk_metadata.append({
                    "paragraph": para_idx + 1,
                    "start_char": start_char,
                    "end_char": start_char + len(current_chunk)
                })
    
    # If no chunks created, create at least one from the whole text
    if not chunks and text.strip():
        chunks = [text.strip()[:chunk_size * 2]]
        chunk_metadata = [{"paragraph": 1, "start_char": 0, "end_char": len(chunks[0])}]
    
    # Create embeddings for each chunk
    for i, chunk in enumerate(chunks):
        if not chunk or len(chunk.strip()) < 10:
            continue
        chunk_id = f"{document_id}_chunk_{i}"
        try:
            embedding = get_embeddings(chunk)
            _embeddings_cache[chunk_id] = embedding
            # Store chunk with document_id for source tracking
            _documents_cache[chunk_id] = chunk
            # Store document source (filename) and metadata for citation
            _document_sources[chunk_id] = document_id
            # Store metadata (paragraph number) for detailed citation
            if i < len(chunk_metadata):
                metadata = chunk_metadata[i]
                # Store metadata as part of source info
                _document_sources[chunk_id] = f"{document_id}|para_{metadata['paragraph']}"
            logger.debug(f"Indexed chunk {chunk_id}: {len(chunk)} chars, paragraph {chunk_metadata[i]['paragraph'] if i < len(chunk_metadata) else 'unknown'}")
        except Exception as e:
            logger.error(f"Error indexing chunk {chunk_id}: {e}")
    
    logger.info(f"Indexed document {document_id} with {len(chunks)} chunks")


def query_rag(query: str, top_k: int = 5, min_similarity: float = 0.15) -> List[Dict[str, Any]]:
    """Query the RAG system."""
    if not _embeddings_cache:
        return []
    
    try:
        query_embedding = get_embeddings(query)
        
        # Compute cosine similarity for all chunks
        similarities = []
        for chunk_id, doc_embedding in _embeddings_cache.items():
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
            )
            # Include all results, we'll filter later if needed
            doc_id = chunk_id.split("_chunk_")[0] if "_chunk_" in chunk_id else None
            # Get source filename and paragraph info
            source_info = _document_sources.get(chunk_id, doc_id)
            # Parse source info (format: "doc_id|para_N" or just "doc_id")
            source = doc_id
            paragraph = None
            if source_info and "|" in source_info:
                parts = source_info.split("|")
                source = parts[0]
                if len(parts) > 1:
                    para_info = parts[1]
                    if para_info.startswith("para_"):
                        paragraph = para_info.replace("para_", "")
            
            # Clean up source name for display
            display_source = source
            if source and source.startswith("bank_doc_"):
                display_source = source.replace("bank_doc_", "").replace("_", " ").replace(".pdf", "").replace(".PDF", "")
            
            # Add paragraph info to source
            if paragraph:
                display_source = f"{display_source} (Paragraph {paragraph})"
            
            similarities.append({
                "chunk_id": chunk_id,
                "similarity": float(similarity),
                "text": _documents_cache.get(chunk_id, ""),
                "document_id": doc_id,
                "source": display_source,  # Add source for citation
                "paragraph": paragraph  # Add paragraph number
            })
        
        # Sort by similarity and return top_k (even if similarity is low)
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        results = similarities[:top_k]
        
        # If no results with good similarity, still return top results
        if not results or (results and results[0]["similarity"] < min_similarity):
            # Return top results anyway, but mark them as low confidence
            return similarities[:top_k] if similarities else []
        
        return results
    except Exception as e:
        logger.error(f"RAG query error: {e}")
        return []


def query_rag_with_context(query: str, document_id: str, top_k: int = 5, min_similarity: float = 0.15) -> List[Dict[str, Any]]:
    """Query the RAG system for a specific document."""
    if not _embeddings_cache:
        return []
    
    try:
        query_embedding = get_embeddings(query)
        
        # Compute cosine similarity only for chunks from the specified document
        similarities = []
        for chunk_id, doc_embedding in _embeddings_cache.items():
            # Filter by document_id
            if not chunk_id.startswith(f"{document_id}_chunk_"):
                continue
                
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
            )
            # Get source filename and paragraph info
            source_info = _document_sources.get(chunk_id, document_id)
            # Parse source info (format: "doc_id|para_N" or just "doc_id")
            source = document_id
            paragraph = None
            if source_info and "|" in source_info:
                parts = source_info.split("|")
                source = parts[0]
                if len(parts) > 1:
                    para_info = parts[1]
                    if para_info.startswith("para_"):
                        paragraph = para_info.replace("para_", "")
            
            # Clean up source name for display
            display_source = source
            if source and source.startswith("bank_doc_"):
                display_source = source.replace("bank_doc_", "").replace("_", " ").replace(".pdf", "").replace(".PDF", "")
            
            # Add paragraph info to source
            if paragraph:
                display_source = f"{display_source} (Paragraph {paragraph})"
            
            # Include all results from this document
            similarities.append({
                "chunk_id": chunk_id,
                "similarity": float(similarity),
                "text": _documents_cache.get(chunk_id, ""),
                "document_id": document_id,
                "source": display_source,  # Add source for citation
                "paragraph": paragraph  # Add paragraph number
            })
        
        # Sort by similarity and return top_k (even if similarity is low)
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        results = similarities[:top_k] if similarities else []
        
        # Always return results if we have any chunks from this document
        return results
    except Exception as e:
        logger.error(f"RAG query error for document {document_id}: {e}")
        return []


def generate_answer(query: str, context_chunks: List[Dict[str, Any]]) -> str:
    """Generate a natural language answer from context chunks."""
    if not context_chunks:
        return "I couldn't find information in the documents. Please make sure documents are loaded and contain text."
    
    # Use all chunks, prioritize by similarity but don't exclude low similarity ones
    # Sort by similarity and take top chunks
    sorted_chunks = sorted(context_chunks, key=lambda x: x.get("similarity", 0), reverse=True)
    relevant_chunks = sorted_chunks[:3]  # Always use top 3 chunks
    
    # If we have chunks, we should provide an answer even if similarity is low
    if not relevant_chunks:
        relevant_chunks = context_chunks[:2]  # Fallback to top 2
    
    # Combine relevant chunks, removing duplicates
    seen_texts = set()
    unique_chunks = []
    for chunk in relevant_chunks:
        text = chunk.get("text", "").strip()
        # Accept shorter texts too, just filter empty ones
        if text and text not in seen_texts and len(text) > 10:
            seen_texts.add(text)
            unique_chunks.append(text)
    
    if not unique_chunks:
        # If no unique chunks, try to get any text from chunks
        for chunk in context_chunks:
            text = chunk.get("text", "").strip()
            if text and len(text) > 10:
                unique_chunks.append(text)
                break
        
        if not unique_chunks:
            return "The document doesn't contain readable text for this question. Please try a different question."
    
    combined_context = "\n\n".join(unique_chunks)
    
    # Simple answer generation based on query type
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    # Get sources from context chunks
    sources = []
    for chunk in context_chunks[:3]:
        source = chunk.get("source", "")
        if source and source not in sources:
            sources.append(source)
    
    # Summary/general questions
    if any(word in query_lower for word in ["summary", "summarize", "what", "what is", "describe", "tell me", "overview", "explain"]):
        # Extract key sentences
        sentences = combined_context.split('. ')
        key_sentences = []
        for sentence in sentences:
            if len(sentence) > 30 and len(sentence) < 300:
                key_sentences.append(sentence.strip())
            if len(key_sentences) >= 5:
                break
        
        if key_sentences:
            answer = "Based on the documents, here's the key information:\n\n"
            answer += ". ".join(key_sentences) + "."
            if sources:
                answer += f"\n\n📄 Sources: {', '.join(sources)}"
            return answer
        else:
            answer = f"Based on the documents:\n\n{combined_context[:500]}{'...' if len(combined_context) > 500 else ''}"
            if sources:
                answer += f"\n\n📄 Sources: {', '.join(sources)}"
            return answer
    
    # Specific questions (who, what, when, where, how, why)
    if any(word in query_lower for word in ["how", "what", "when", "where", "why", "who", "which", "how many", "how much"]):
        # Try to find sentences that contain query words
        sentences = combined_context.split('. ')
        relevant_sentences = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Check if sentence contains any query word or is related
            if any(word in sentence_lower for word in query_words) or len(query_words.intersection(set(sentence_lower.split()))) > 0:
                if len(sentence.strip()) > 20:
                    relevant_sentences.append(sentence.strip())
        
        if relevant_sentences:
            answer = "Based on the documents:\n\n"
            answer += ". ".join(relevant_sentences[:3]) + "."
            if sources:
                answer += f"\n\n📄 Sources: {', '.join(sources)}"
            return answer
        else:
            # Return most relevant chunk
            answer = f"Based on the documents:\n\n{unique_chunks[0][:400]}{'...' if len(unique_chunks[0]) > 400 else ''}"
            if sources:
                answer += f"\n\n📄 Sources: {', '.join(sources)}"
            return answer
    
    # Yes/No questions
    if any(word in query_lower for word in ["is", "are", "does", "do", "can", "will", "should", "must"]):
        # Look for affirmative/negative indicators
        combined_lower = combined_context.lower()
        if any(word in combined_lower for word in ["yes", "is", "are", "does", "do", "can", "will"]):
            answer = f"Based on the documents, yes:\n\n{unique_chunks[0][:300]}{'...' if len(unique_chunks[0]) > 300 else ''}"
            if sources:
                answer += f"\n\n📄 Sources: {', '.join(sources)}"
            return answer
        else:
            answer = f"Based on the documents:\n\n{unique_chunks[0][:300]}{'...' if len(unique_chunks[0]) > 300 else ''}"
            if sources:
                answer += f"\n\n📄 Sources: {', '.join(sources)}"
            return answer
    
    # Default: return combined context with explanation
    # Clean up the context (remove excessive whitespace, fix formatting)
    cleaned_context = " ".join(combined_context.split())
    
    # Always ensure we have content
    if not cleaned_context or len(cleaned_context.strip()) < 10:
        if unique_chunks:
            cleaned_context = unique_chunks[0]
        elif context_chunks:
            cleaned_context = context_chunks[0].get("text", "")[:500]
        else:
            cleaned_context = "Information from documents."
    
    if len(cleaned_context) > 600:
        # Try to find a good breaking point
        sentences = cleaned_context.split('. ')
        answer_parts = []
        total_len = 0
        for sentence in sentences:
            if total_len + len(sentence) < 600:
                answer_parts.append(sentence)
                total_len += len(sentence)
            else:
                break
        answer = ". ".join(answer_parts) + "."
    else:
        answer = cleaned_context
    
    # Final safety check - always return something
    if not answer or len(answer.strip()) < 5:
        answer = unique_chunks[0] if unique_chunks else (context_chunks[0].get("text", "")[:400] if context_chunks else "Information from documents.")
    
    # Build answer with sources
    answer_text = f"Based on the documents, here's what I found:\n\n{answer}"
    
    if sources:
        answer_text += f"\n\n📄 Sources: {', '.join(sources)}"
    
    return answer_text
