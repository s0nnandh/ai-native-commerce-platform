# Generate the top k=3 embedded documents for each of the questions in a text input file
# and write the output to an excel file 

from langchain_chroma import Chroma
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
import argparse
from dotenv import load_dotenv
import os

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

def get_k_top_documents(query: str, vectorstore: Chroma, k: int = 3, th: float = 0.75) -> list[Document]:
    """Get top k documents for a query crossing threshold"""
    docs = vectorstore.similarity_search_with_relevance_scores(query, k=k)
    docs = [doc for doc, score in docs if score > th]
    return docs

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

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Ingest Excel data into ChromaDB')
    parser.add_argument('--input_file', type=str, required=True, help='Path to the file to get questions')
    parser.add_argument('--output_file', type=str, required=True, help='Path to the output file')
    parser.add_argument('--collection', '-c', default='evergrow_skincare_catalog',
                       help='ChromaDB collection name')
    parser.add_argument('--persist_dir', '-p', default='./data/chroma_db',
                       help='ChromaDB persistence directory')
    parser.add_argument('--k', type=int, default=3, help='Number of top documents to retrieve')
    parser.add_argument('--th', type=float, default=0.75, help='Similarity threshold')
    args = parser.parse_args()

    load_dotenv()

    # Load the vectorstore
    vectorstore = Chroma(persist_directory=args.persist_dir, collection_name=args.collection, embedding_function=OpenAIEmbeddings())

    # Read the questions from the input file
    text_data = load_text_data(args.input_file)
    
    questions = text_data.split('\n')

    # Generate the top k=3 embedded documents for each of the questions
    # and write the output to an excel file
    import pandas as pd
    df = pd.DataFrame(columns=['Question', 'Top 1', 'Top 2', 'Top 3'])
    row_list = []
    for question in questions:
        print(f"Processing question: {question}")
        docs = get_k_top_documents(question, vectorstore, args.k, args.th)
        len_docs = len(docs) - 1
        row_list.append({'Question': question, 'Top 1': docs[0].page_content, 'Top 2': docs[min(len_docs, 1)].page_content, 'Top 3': docs[min(len_docs, 2)].page_content})
    df = pd.DataFrame(row_list)
    # Write the output to an excel file
    df.to_excel(args.output_file, index=False)

if __name__ == "__main__":
    main()