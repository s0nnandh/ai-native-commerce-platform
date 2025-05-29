import pandas as pd
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
import os
import argparse
from typing import List, Dict, Any
from dotenv import load_dotenv

PROCESSING_MAP = {
    'product': 'process_product_data',
    'review': 'process_review_data', 
    'ticket': 'process_ticket_data',
    'description': 'process_description_data'
}

# Method to load env file
def load_env_file() -> None:
    """Load environment variables from a .env file"""
    try:
        load_dotenv()
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

def load_text_data(file_path: str) -> str:
    """Load text file and return content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        print(f"Loaded text file: {file_path}")
        return content
    except Exception as e:
        print(f"Error loading text file: {e}")
        raise

def normalize_ingredients(ingredients: str) -> str:
    """Normalize ingredients string to list of ingredients"""
    word_ingredients = []
    for ingredient in ingredients.split(';'):
        all = ingredient.strip().split('(')
        for x in all:
            word_ingredients.append(x.replace(')', '').strip())
    return "|".join([ing.replace(' ', '-').lower() for ing in word_ingredients]) 

def normalize_tags(tags: str) -> str:
    """Normalize tags string to list of tags"""
    return tags.replace(' ', '-').lower()

def get_value(row: Dict[str, str], key: str) -> str:
        """Helper function to get value from row, handling missing keys"""
        v = row.get(key, '')
        if isinstance(v, str):
            return v.strip()
        return v

def process_product_data(df: pd.DataFrame, doc_type: str = None) -> List[Document]:
    """Convert DataFrame rows to LangChain Documents with formatted text"""
    documents = []
    
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
Tags: {", ".join(tags.split('|') if isinstance(row['tags'], str) else [] )}."""
        # Create metadata dictionary
        metadata = {
            'doc_type': doc_type,
            'product_id': product_id,
            'name': name,
            'category': category.split('/')[-1].strip().replace(' ', '-').lower(),
            'description': description,
            'top_ingredients': normalize_ingredients(top_ingredients),
            'tags': normalize_tags(tags),
            'price_usd': float(price),
            'margin_percent': float(margin)
        }
                
        # Create Document object
        doc = Document(
            id=f"{product_id}_0",
            page_content=text_content,
            metadata=metadata
        )
        
        documents.append(doc)
    print(documents)

    return documents

def process_review_data(df: pd.DataFrame, doc_type: str) -> List[Document]:
    """Convert DataFrame rows to LangChain Documents for product reviews"""
    documents = []
    
    for index, row in df.iterrows():
        # Extract data from row
        review_id = get_value(row, 'Review ID')
        reviewer = get_value(row, 'Reviewer')
        product = get_value(row, 'Product')
        rating = get_value(row, 'Rating')
        review_text = get_value(row, 'Review')
        annotated_rating = get_value(row, 'Annotated Rating')

        
        # Format text content
        text_content = f"""Product: {product}
Reviewer: {reviewer}
Rating: {annotated_rating}
Review: {review_text}"""
        
        # Parse reviewer info (assuming format: "Name - Skin Type (Age)")
        reviewer_name = reviewer.split(' – ')[0] if ' – ' in reviewer else reviewer
        reviewer_details = reviewer.split(' – ')[1] if ' – ' in reviewer else ""
        
        # Extract age if available
        age = None
        tags = None
        if reviewer_details:
            if '(' in reviewer_details and ')' in reviewer_details:
                parts = reviewer_details.split('(')
                tag_list = parts[0].replace('/', ',').replace('&', ',').split(',')
                tags = "|".join([tag.strip().replace(' ', '-').lower() for tag in tag_list])
                age_str = parts[1].replace(')', '').strip()
                try:
                    age = int(age_str)
                except:
                    pass
        
        # Create metadata dictionary
        metadata = {
            'doc_type': doc_type,
            'review_id': review_id,
            'reviewer_name': reviewer_name,
            'reviewer_full': reviewer,
            'reviewer_age': age,
            'product_name': product,
            'tags': tags,
            'rating_display': rating,
            'annotated_rating': annotated_rating,
            'sentiment': 'positive' if int(annotated_rating[0]) >= 4 else 'neutral' if int(annotated_rating[0]) == 3 else 'negative'
        }
        
        # Create Document object
        doc = Document(
            id=f"{review_id}_0",
            page_content=text_content,
            metadata=metadata
        )
        
        documents.append(doc)
    
    print(documents)
    
    return documents


def process_ticket_data(df: pd.DataFrame, doc_type: str) -> List[Document]:
    """Convert DataFrame rows to LangChain Documents for customer support tickets"""
    documents = []
    
    for index, row in df.iterrows():
        # Extract data from row
        ticket_id = get_value(row, 'Ticket ID')
        customer_message = get_value(row, 'Customer Message')
        support_response = get_value(row, 'Support Response')
        
        # Format text content
        text_content = f"""
        Customer Issue: {customer_message}
        Support Response: {support_response}
"""
        
        # Try to Analyze ticket characteristics
        issue_type = "unknown"
        if any(word in customer_message.lower() for word in ['delivery', 'shipped', 'arrived', 'package']):
            issue_type = "shipping"
        elif any(word in customer_message.lower() for word in ['refund', 'return', 'money']):
            issue_type = "refund"
        elif any(word in customer_message.lower() for word in ['product', 'quality', 'broken']):
            issue_type = "product_quality"
        elif any(word in customer_message.lower() for word in ['account', 'login', 'password']):
            issue_type = "account"
        
        urgency = "high" if any(word in customer_message.lower() for word in ['urgent', 'asap', 'soon', 'immediately']) else "normal"
        
        # Create metadata dictionary
        metadata = {
            'doc_type': doc_type,
            'ticket_id': ticket_id,
            'issue_type': issue_type,
            'urgency': urgency,
        }
        
        # Create Document object
        doc = Document(
            id=f"{ticket_id}_0",
            page_content=text_content,
            metadata=metadata
        )
        
        documents.append(doc)
    
    return documents

def process_description_data(text_content: str, doc_type: str, file_path: str) -> List[Document]:
    """Convert text file content to LangChain Documents for company/product descriptions"""
    
    # For now, treating entire content as single document
    # Could be enhanced to split by sections/paragraphs if needed
    
    # Analyze content characteristics
    # word_count = len(text_content.split())
    # char_count = len(text_content)
    # paragraph_count = len([p for p in text_content.split('\n\n') if p.strip()])
    
    # Extract some basic insights
    # contains_product_info = any(word in text_content.lower() for word in ['product', 'serum', 'cream', 'skincare'])
    # contains_company_info = any(word in text_content.lower() for word in ['company', 'brand', 'founded', 'mission'])
    # contains_ingredients = any(word in text_content.lower() for word in ['ingredient', 'formula', 'vitamin', 'acid'])
    
    # Create metadata dictionary
    metadata = {
        'doc_type': doc_type,
        'source_file': os.path.basename(file_path),
        'file_path': file_path
    }
    
    # Create Document object
    doc = Document(
        # TODO: To check if renaming is required
        id=f"{doc_type}_0",
        page_content=text_content,
        metadata=metadata
    )
    
    return [doc]


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

def process_file(file_path: str, doc_type: str) -> List[Document]:
    """Process file based on document type"""
    
    if doc_type not in PROCESSING_MAP:
        raise ValueError(f"Unsupported document type: {doc_type}. Supported types: {list(PROCESSING_MAP.keys())}")
    
    processing_func_name = PROCESSING_MAP[doc_type]
    processing_func = globals()[processing_func_name]
    
    if doc_type == 'description':
        # Handle text file
        text_content = load_text_data(file_path)
        documents = processing_func(text_content, doc_type, file_path)
    else:
        # Handle Excel files
        df = load_excel_data(file_path)
        documents = processing_func(df, doc_type)
    
    return documents

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

# def main(excel_file_path: str, collection_name: str = "products", doc_type: str = None):
#     """Main function to orchestrate the ingestion process"""
    
#     print("Starting Excel to ChromaDB ingestion process...")
    
#     # Step 1: Load Excel data
#     df = load_excel_data(excel_file_path)
    
#     # Step 2: Process data into Documents
#     print("Processing product data...")
#     documents = process_product_data(df, doc_type)
    
#     # Preview first document
#     print(f"\nSample document text:\n{documents[0].page_content}")
#     print(f"\nSample metadata:\n{documents[0].metadata}")
    
#     # Step 3: Setup ChromaDB vectorstore
#     print("\nSetting up ChromaDB vectorstore...")
#     vectorstore = setup_chroma_vectorstore(collection_name)
    
#     # Step 4: Ingest documents
#     print("Ingesting documents into ChromaDB...")
#     ingest_documents_to_chroma(documents, vectorstore)
    
#     print(f"\n✅ Ingestion complete! {len(documents)} products added to ChromaDB collection '{collection_name}'")
    
#     return vectorstore

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
    parser.add_argument('--file', type=str, required=True, help='Path to the file to ingest')
    parser.add_argument('--doc_type', type=str, required=True, help='Document type to add to metadata')
    parser.add_argument('--collection', '-c', default='evergrow_skincare_catalog',
                       help='ChromaDB collection name')
    parser.add_argument('--persist_dir', '-p', default='./data/chroma_db',
                       help='ChromaDB persistence directory')
    
    # Parse arguments
    args = parser.parse_args()
    
    load_env_file()
    
    # Make sure to set your OpenAI API key
    # os.environ["OPENAI_API_KEY"] = "your-api-key-here"
    
    try:
        # Process the file
        documents = process_file(args.file, args.doc_type)
        
        # Preview first document
        print(f"\nProcessed {len(documents)} documents")
        print(f"\nSample document text:\n{documents[0].page_content[:300]}...")
        print(f"\nSample metadata:\n{documents[0].metadata}")
        
        # Setup ChromaDB vectorstore
        print(f"\nSetting up ChromaDB vectorstore...")
        vectorstore = setup_chroma_vectorstore(args.collection, args.persist_dir)
        
        # Ingest documents
        print("Ingesting documents into ChromaDB...")
        # ingest_documents_to_chroma(documents, vectorstore)
        
        print(f"\n✅ Ingestion complete! {len(documents)} {args.doc_type} documents added to ChromaDB collection '{args.collection}'")
        
        # Example query
        # query_example(vectorstore, "serum for brightening skin", k=3)
        # search_by_metadata(vectorstore, ["Serum"])
        
    except Exception as e:
        print(f"Error in main execution: {e}")
