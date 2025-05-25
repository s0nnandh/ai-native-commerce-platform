import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)

class VectorStore:
    """Utility class for interacting with ChromaDB vector store."""
    
    def __init__(self, 
                 persist_directory: str = None, 
                 collection_name: str = "product_data"):
        """Initialize the vector store.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the collection to use
        """
        self.persist_directory = persist_directory or os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
        self.collection_name = collection_name or os.getenv("CHROMA_COLLECTION_NAME", "product_data")
        
        # Create directory if it doesn't exist
        if self.persist_directory and not os.path.exists(self.persist_directory):
            os.makedirs(self.persist_directory)
            
        # Initialize client
        if self.persist_directory:
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
        else:
            self.client = chromadb.Client(Settings(anonymized_telemetry=False))
            
        # Get or create collection
        self.collection = self.client.get_or_create_collection(name=self.collection_name)
        logger.info(f"Initialized vector store with collection: {self.collection_name}")
    
    def add_documents(self, 
                      documents: List[str], 
                      metadatas: Optional[List[Dict[str, Any]]] = None, 
                      ids: Optional[List[str]] = None) -> None:
        """Add documents to the vector store.
        
        Args:
            documents: List of document texts
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of document IDs
        """
        if not ids:
            import uuid
            ids = [str(uuid.uuid4()) for _ in documents]
            
        if not metadatas:
            metadatas = [{} for _ in documents]
            
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"Added {len(documents)} documents to collection {self.collection_name}")
    
    def query(self, 
              query_text: str, 
              n_results: int = 3, 
              where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Query the vector store.
        
        Args:
            query_text: Text to query
            n_results: Number of results to return
            where: Optional filter criteria
            
        Returns:
            Query results
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where
        )
        return results
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection.
        
        Returns:
            Collection statistics
        """
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count
        }
