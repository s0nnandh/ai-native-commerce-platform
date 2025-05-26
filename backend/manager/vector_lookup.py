"""
Simple ChromaDB vector store manager for similarity search.
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import structlog
import chromadb
from langchain.schema import Document

logger = structlog.get_logger()


class VectorStoreManager:
    """Simple ChromaDB vector store manager."""
    
    def __init__(
        self,
        collection_name: str = "corpus",
        persist_directory: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None
    ):
        """Initialize vector store manager."""
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        
        # Connect to ChromaDB
        if host and port:
            self.client = chromadb.HttpClient(host=host, port=port)
        else:
            if not persist_directory:
                project_root = Path(__file__).parent.parent
                persist_directory = str(project_root / "data" / "chroma_db")
            self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get collection
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info("chromadb_connected", 
                       collection=self.collection_name,
                       documents=self.collection.count())
        except Exception as e:
            logger.error("chromadb_collection_error", error=str(e))
            raise ValueError(f"Collection '{self.collection_name}' not found")
    
    def similarity_search(
        self,
        query: str,
        k: int = 25,
        filter: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None
    ) -> List[Document]:
        """
        Perform similarity search using ChromaDB's built-in functions.
        
        Args:
            query: Search query text
            k: Number of results to return
            filter: Metadata filters
            score_threshold: Minimum similarity score (0.0 to 1.0)
            
        Returns:
            List of Document objects
        """
        if not self.collection:
            return []
        
        try:
            # Use ChromaDB's query method with built-in distance calculation
            results = self.collection.query(
                query_texts=[query],
                n_results=k,
                where=filter,
                include=['documents', 'metadatas', 'distances']
            )
            
            documents = []
            if results['documents'] and results['documents'][0]:
                for i, doc_content in enumerate(results['documents'][0]):
                    # Get metadata
                    metadata = {}
                    if results['metadatas'] and results['metadatas'][0]:
                        metadata = results['metadatas'][0][i] or {}
                    
                    # Add similarity score (ChromaDB returns distances, lower = more similar)
                    if results['distances'] and results['distances'][0]:
                        distance = results['distances'][0][i]
                        # Convert distance to similarity score
                        similarity_score = max(0.0, 1.0 - distance)
                        metadata['score'] = similarity_score
                        
                        # Filter by threshold
                        if score_threshold and similarity_score < score_threshold:
                            continue
                    
                    documents.append(Document(
                        page_content=doc_content,
                        metadata=metadata
                    ))
            
            logger.info("similarity_search_success",
                       query_len=len(query),
                       results=len(documents))
            
            return documents
            
        except Exception as e:
            logger.error("similarity_search_failed", error=str(e))
            return []


def create_vector_store_manager() -> VectorStoreManager:
    """Create vector store manager from environment variables."""
    chroma_host = os.getenv('CHROMA_HOST')
    chroma_port = os.getenv('CHROMA_PORT')
    
    if chroma_host and chroma_port:
        return VectorStoreManager(host=chroma_host, port=int(chroma_port))
    else:
        persist_dir = os.getenv('CHROMA_PERSIST_DIR')
        return VectorStoreManager(persist_directory=persist_dir)


# Global instance
vector_store_manager = create_vector_store_manager()


def get_vector_store() -> VectorStoreManager:
    """Get the global vector store manager instance."""
    return vector_store_manager