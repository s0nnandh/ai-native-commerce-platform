"""
LangChain Chroma vector store manager with dual mode support.
Supports both file-based (development) and client-based (production) connections.
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import structlog
import chromadb
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

logger = structlog.get_logger()


class VectorStoreManager:
    """
    LangChain Chroma vector store manager with dual mode support.
    Automatically detects file-based vs client-based mode from environment.
    """
    
    def __init__(
        self,
        collection_name: str = "evergrow_skincare_catalog",
        persist_directory: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None
    ):
        """
        Initialize vector store manager with automatic mode detection.
        
        Args:
            collection_name: ChromaDB collection name
            persist_directory: Path for file-based mode
            host: ChromaDB server host for client mode
            port: ChromaDB server port for client mode
        """
        self.collection_name = collection_name
        self.connection_mode = None
        
        # Initialize embeddings (same as ingestion)
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Determine connection mode and initialize
        if host and port:
            self._init_client_mode(host, port)
        else:
            self._init_file_mode(persist_directory)
    
    def _init_client_mode(self, host: str, port: int):
        """Initialize in client mode (HTTP connection to ChromaDB server)."""
        try:
            # Create ChromaDB HTTP client
            chroma_client = chromadb.HttpClient(host=host, port=port)
            
            # Initialize LangChain Chroma with client
            self.vectorstore = Chroma(
                client=chroma_client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings
            )
            
            self.connection_mode = "client"
            logger.info("chroma_client_mode_connected", 
                       host=host, 
                       port=port,
                       collection=self.collection_name)
                       
        except Exception as e:
            logger.error("chroma_client_mode_failed", 
                        host=host, 
                        port=port, 
                        error=str(e))
            raise ConnectionError(f"Failed to connect to ChromaDB server at {host}:{port}: {str(e)}")
    
    def _init_file_mode(self, persist_directory: Optional[str]):
        """Initialize in file mode (direct file access)."""
        try:
            # Set default persist directory
            if not persist_directory:
                project_root = Path(__file__).parent.parent
                persist_directory = str(project_root / "data" / "chroma_db")
                print(persist_directory)
            
            # Initialize LangChain Chroma with file persistence
            self.vectorstore = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings,
                collection_name=self.collection_name
            )
            
            self.connection_mode = "file"
            logger.info("chroma_file_mode_connected", 
                       persist_dir=persist_directory,
                       collection=self.collection_name)
            
            # run limit query in embeddings
            row_count = self.vectorstore._collection.count()
            logger.info("chroma_file_mode_row_count",
                       persist_dir=persist_directory,
                       collection=self.collection_name,
                       row_count=row_count)
                       
        except Exception as e:
            logger.error("chroma_file_mode_failed", 
                        persist_dir=persist_directory, 
                        error=str(e))
            raise ConnectionError(f"Failed to connect to ChromaDB files at {persist_directory}: {str(e)}")
    
    def _convert_simple_filter_to_chroma(self, simple_filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convert simple filter format to ChromaDB's expected query format.
        
        Args:
            simple_filter: Simple filter dict like {"category": "moisturizer", "tags": ["acne", "hydrating"]}
            
        Returns:
            ChromaDB compatible filter dict or None if conversion fails
            
        Examples:
            Input:  {"category": "moisturizer"}
            Output: {"category": {"$eq": "moisturizer"}}
            
            Input:  {"category": "moisturizer", "tags": ["acne", "hydrating"]}
            Output: {"$and": [{"category": {"$eq": "moisturizer"}}, {"tags": {"$in": ["acne", "hydrating"]}}]}
        """
        if not simple_filter:
            return None
            
        try:
            chroma_conditions = []
            
            for key, value in simple_filter.items():
                if key in ['top_ingredients', 'tags']:
                    # Support is pending https://github.com/chroma-core/chroma/issues/3415
                    continue
                if key in ['price_usd']:
                    # Handled in manual filter
                    continue
                if value is None:
                    # Skip null values
                    continue
                elif isinstance(value, list):
                    if value:  # Non-empty list
                        # List values: check if metadata list contains any of these values
                        chroma_conditions.append({key: {"$in": value}})
                    # Skip empty lists
                elif isinstance(value, (str, int, float, bool)):
                    # Single values: exact match
                    chroma_conditions.append({key: {"$eq": value}})
                else:
                    # Unknown type, try to convert to string
                    logger.warning("unknown_filter_value_type", 
                                 key=key, 
                                 value=value, 
                                 type=type(value).__name__)
                    chroma_conditions.append({key: {"$eq": str(value)}})
            
            # Return appropriate format based on number of conditions
            if len(chroma_conditions) == 0:
                return None
            elif len(chroma_conditions) == 1:
                return chroma_conditions[0]
            else:
                return {"$and": chroma_conditions}
                
        except Exception as e:
            logger.error("filter_conversion_failed", 
                        simple_filter=simple_filter, 
                        error=str(e))
            return None
    
    def similarity_search(
        self,
        query: str,
        k: int = 25,
        filter: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None
    ) -> List[Document]:
        """
        Perform similarity search using LangChain Chroma's built-in methods.
        Works identically in both client and file modes.
        
        Args:
            query: Search query text
            k: Number of results to return
            filter: Metadata filters (e.g., {"category": "serum"})
            score_threshold: Minimum relevance score (0.0 to 1.0)
            
        Returns:
            List of Document objects with metadata
        """
        try:
            chroma_filter = self._convert_simple_filter_to_chroma(filter)
            if score_threshold:
                # Use similarity_search_with_relevance_scores for threshold filtering
                docs_with_scores = self.vectorstore.similarity_search_with_relevance_scores(
                    query=query,
                    k=k,
                    filter=chroma_filter,
                    score_threshold=score_threshold
                )
                # Extract documents and add scores to metadata
                documents = []
                for doc, score in docs_with_scores:
                    doc.metadata['score'] = score
                    documents.append(doc)
                
                # sort on the basis of score
                documents.sort(key=lambda x: x.metadata['score'], reverse=True)

                return documents
            else:
                # Use regular similarity_search
                return self.vectorstore.similarity_search(
                    query=query,
                    k=k,
                    filter=chroma_filter
                )
            
        except Exception as e:
            logger.error("similarity_search_failed", 
                        query=query[:50], 
                        connection_mode=self.connection_mode,
                        error=str(e))
            return []
    
    def similarity_search_with_scores(
        self,
        query: str,
        k: int = 25,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Document, float]]:
        """
        Perform similarity search and return documents with relevance scores.
        Works identically in both client and file modes.
        
        Args:
            query: Search query text
            k: Number of results to return
            filter: Metadata filters
            
        Returns:
            List of (Document, relevance_score) tuples
        """
        try:
            choma_filter = self._convert_simple_filter_to_chroma(filter)
            return self.vectorstore.similarity_search_with_relevance_scores(
                query=query,
                k=k,
                filter=choma_filter
            )
        except Exception as e:
            logger.error("similarity_search_with_scores_failed", 
                        query=query[:50], 
                        connection_mode=self.connection_mode,
                        error=str(e))
            return []
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get information about the current connection mode."""
        return {
            "mode": self.connection_mode,
            "collection_name": self.collection_name,
            "embedding_model": "text-embedding-ada-002"
        }


def create_vector_store_manager() -> VectorStoreManager:
    """
    Create vector store manager with automatic mode detection from environment.
    
    Environment Variables:
        CHROMA_HOST: ChromaDB server host (enables client mode)
        CHROMA_PORT: ChromaDB server port (enables client mode)
        CHROMA_PERSIST_DIR: Directory for file mode (optional)
        CHROMA_COLLECTION_NAME: Collection name (optional, defaults to 'corpus')
    
    Returns:
        Configured VectorStoreManager instance
    """
    # Check for client mode environment variables
    chroma_host = os.getenv('CHROMA_HOST')
    chroma_port_str = os.getenv('CHROMA_PORT')
    
    # Get optional configuration
    persist_dir = os.getenv('CHROMA_PERSIST_DIR')
    collection_name = os.getenv('CHROMA_COLLECTION_NAME', 'corpus')
    
    if chroma_host and chroma_port_str:
        # Client mode (production)
        try:
            chroma_port = int(chroma_port_str)
            logger.info("initializing_vector_store_client_mode", 
                       host=chroma_host, 
                       port=chroma_port)
            return VectorStoreManager(
                collection_name=collection_name,
                host=chroma_host,
                port=chroma_port
            )
        except ValueError:
            logger.error("invalid_chroma_port", port=chroma_port_str)
            raise ValueError(f"Invalid CHROMA_PORT: {chroma_port_str}")
    else:
        # File mode (development)
        logger.info("initializing_vector_store_file_mode", 
                   persist_dir=persist_dir)
        return VectorStoreManager(
            collection_name=collection_name,
            persist_directory=persist_dir
        )


# Global instance
vector_store_manager = create_vector_store_manager()


def get_vector_store() -> VectorStoreManager:
    """Get the global vector store manager instance."""
    return vector_store_manager