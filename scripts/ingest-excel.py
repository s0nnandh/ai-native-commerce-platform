import pandas as pd
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
import os
import argparse
from typing import List, Dict, Any
from dotenv import load_dotenv

# Method to load env file
def load_env_file() -> None:
    """Load environment variables from a .env file"""
    try:
        file_path = os.path.join(os.getcwd(), 'scripts', '.env')
        print(file_path)
        load_dotenv(file_path)
        print("Environment variables loaded successfully.")
    except Exception as e:
        print(f"Error loading environment variables: {e}")
        raise

def load_excel_data(file_path: str) -> pd.DataFrame:
    """Load Excel file and return DataFrame"""
    try:
        df = pd.read_excel(file_path)
        print(f"Loaded {len(df)} rows from {file_path}")
        return df
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        raise

def process_product_data(df: pd.DataFrame, doc_type: str = None) -> List[Document]:
    """Convert DataFrame rows to LangChain Documents with formatted text"""
    documents = []

    def get_value(row: Dict[str, str], key: str) -> str:
        """Helper function to get value from row, handling missing keys"""
        v = row.get(key, '')
        if isinstance(v, str):
            return v.strip()
        return v
    
    for index, row in df.iterrows():
        # Extract data from row
        product_id = get_value(row, 'product_id')
        name = get_value(row, 'name')
        category = get_value(row, 'category')
        description = get_value(row, 'description')
        top_ingredients = get_value(row, 'top_ingredients')
        tags = get_value(row, 'tags')
        price = get_value(row, 'price (USD)')
        margin = get_value(row, 'margin (%)')

        
        # Format text as specified
        text_content = f"""Product Name: {name} | Category: {category}.
Description: {description}.
Top Ingredients: {", ".join(top_ingredients.split(';') if isinstance(row['top_ingredients'], str) else [])}.
Tags: {", ".join(tags.split('|') if isinstance(row['tags'], str) else [])}."""
        
        # Create metadata dictionary
        metadata = {
            'product_id': product_id,
            'name': name,
            'category': category,
            'description': description,
            'top_ingredients': top_ingredients,
            'tags': tags,
            'price_usd': float(price),
            'margin_percent': float(margin)
        }
        
        # Add doc_type to metadata if provided
        if doc_type:
            metadata['doc_type'] = doc_type
        
        # Create Document object
        doc = Document(
            id=f"{product_id}_0",
            page_content=text_content,
            metadata=metadata
        )
        
        documents.append(doc)
    print(documents[0])

    return documents

def setup_chroma_vectorstore(collection_name: str = "products", persist_directory: str = "./data/chroma_db") -> Chroma:
    """Initialize ChromaDB vectorstore with OpenAI embeddings"""
    
    # Ensure OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("Please set your OPENAI_API_KEY environment variable")
    
    # Initialize OpenAI embeddings (ada-002)
    embeddings = OpenAIEmbeddings(
        model="text-embedding-ada-002",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Initialize ChromaDB client
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_directory
    )
    
    return vectorstore

def ingest_documents_to_chroma(documents: List[Document], vectorstore: Chroma) -> None:
    """Add documents to ChromaDB vectorstore"""
    try:
        # Add documents to vectorstore
        vectorstore.add_documents(documents)
        print(f"Successfully added {len(documents)} documents to ChromaDB")
        
        # Persist the vectorstore
        # vectorstore.persist()
        print("ChromaDB collection persisted successfully")
        
    except Exception as e:
        print(f"Error adding documents to ChromaDB: {e}")
        raise

def ingest_text_to_chroma(text: str, vectorstore: Chroma) -> None:
    """Add text to ChromaDB vectorstore"""
    try:
        # Add text to vectorstore
        vectorstore.add_texts([text])
        print(f"Successfully added text to ChromaDB")

        # Persist the vectorstore
        # vectorstore.persist()
        print("ChromaDB collection persisted successfully")

    except Exception as e:
        print(f"Error adding text to ChromaDB: {e}")
        raise

def main(excel_file_path: str, collection_name: str = "products", doc_type: str = None):
    """Main function to orchestrate the ingestion process"""

    load_env_file()
    
    print("Starting Excel to ChromaDB ingestion process...")
    
    # Step 1: Load Excel data
    df = load_excel_data(excel_file_path)
    
    # Step 2: Process data into Documents
    print("Processing product data...")
    documents = process_product_data(df, doc_type)
    
    # Preview first document
    print(f"\nSample document text:\n{documents[0].page_content}")
    print(f"\nSample metadata:\n{documents[0].metadata}")
    
    # Step 3: Setup ChromaDB vectorstore
    print("\nSetting up ChromaDB vectorstore...")
    vectorstore = setup_chroma_vectorstore(collection_name)
    
    # Step 4: Ingest documents
    print("Ingesting documents into ChromaDB...")
    ingest_documents_to_chroma(documents, vectorstore)
    
    print(f"\n✅ Ingestion complete! {len(documents)} products added to ChromaDB collection '{collection_name}'")
    
    return vectorstore

def query_example(vectorstore: Chroma, query: str, k: int = 3):
    """Example function to query the vectorstore"""
    print(f"\nQuerying: '{query}'")
    results = vectorstore.similarity_search(query, k=k)
    
    for i, doc in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Product: {doc.metadata['name']}")
        print(f"Category: {doc.metadata['category']}")
        print(f"Price: ${doc.metadata['price_usd']}")
        print(f"Content: {doc.page_content[:200]}...")


# Additional utility functions

def update_collection(excel_file_path: str, collection_name: str = "products", mode: str = "append", doc_type: str = None):
    """
    Update existing collection with new data
    mode: 'append' to add new documents, 'replace' to replace entire collection
    """
    df = load_excel_data(excel_file_path)
    documents = process_product_data(df, doc_type)
    vectorstore = setup_chroma_vectorstore(collection_name)
    
    if mode == "replace":
        # Clear existing collection
        vectorstore.delete_collection()
        vectorstore = setup_chroma_vectorstore(collection_name)
    
    ingest_documents_to_chroma(documents, vectorstore)
    return vectorstore

def search_by_metadata(vectorstore: Chroma, category_list: list[str], k: int = 5):
    """Search documents by metadata filters"""
    # Note: ChromaDB filtering syntax may vary, adjust as needed

    category_filter = {"category": {"$in": category_list}}
    # author_filter = {"author": {"$in": author_list}}
    # published_filter = {"published": {"$in": published_list}}

    combined_filter = {
    "$and": [
        category_filter,
    ]
}

    results = vectorstore.similarity_search("", k=k, filter=category_filter)
    print(results)

    for i, doc in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Product: {doc.metadata['name']}")
        print(f"Category: {doc.metadata['category']}")
        print(f"Price: ${doc.metadata['price_usd']}")
        print(f"Content: {doc.page_content[:200]}...")

    return results

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Ingest Excel data into ChromaDB')
    parser.add_argument('--excel_file', type=str, required=True, help='Path to the Excel file')
    parser.add_argument('--doc_type', type=str, required=True, help='Document type to add to metadata')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Collection name remains the same
    COLLECTION_NAME = "evergrow_skincare_catalog"
    
    # Make sure to set your OpenAI API key
    # os.environ["OPENAI_API_KEY"] = "your-api-key-here"
    
    try:
        # Run the ingestion process
        vectorstore = main(args.excel_file, COLLECTION_NAME, args.doc_type)
        
        # Example query
        query_example(vectorstore, "serum for brightening skin", k=3)
        search_by_metadata(vectorstore, ["Serum"])
        
    except Exception as e:
        print(f"Error in main execution: {e}")
