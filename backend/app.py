import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import chromadb
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph
from langgraph.graph.message import MessageState
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize OpenAI client
llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo"),
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Initialize ChromaDB client
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(
    name=os.getenv("CHROMA_COLLECTION_NAME", "product_data")
)

# Define Lang-graph stateful graph
def generate_response(state):
    """Generate a response using the LLM."""
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": messages + [response]}

def retrieve_context(state):
    """Retrieve relevant context from the vector store."""
    messages = state["messages"]
    query = messages[-1].content
    
    # Query the vector store
    results = collection.query(
        query_texts=[query],
        n_results=3
    )
    
    # Add context to the state
    return {
        "messages": messages,
        "context": results
    }

def enhance_prompt(state):
    """Enhance the prompt with retrieved context."""
    messages = state["messages"]
    context = state.get("context", {"documents": []})
    
    # Create an enhanced prompt with context
    last_message = messages[-1]
    enhanced_content = f"""
    Context information:
    {context}
    
    User query:
    {last_message.content}
    """
    
    # Replace the last message with the enhanced one
    enhanced_message = last_message.copy()
    enhanced_message.content = enhanced_content
    
    return {"messages": messages[:-1] + [enhanced_message]}

# Define the graph
builder = StateGraph(MessageState)

# Add nodes
builder.add_node("retrieve_context", retrieve_context)
builder.add_node("enhance_prompt", enhance_prompt)
builder.add_node("generate_response", generate_response)

# Add edges
builder.add_edge("retrieve_context", "enhance_prompt")
builder.add_edge("enhance_prompt", "generate_response")
builder.set_entry_point("retrieve_context")

# Compile the graph
graph = builder.compile()

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint for chat interactions."""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Initialize state with user message
        from langchain_core.messages import HumanMessage
        initial_state = {"messages": [HumanMessage(content=user_message)]}
        
        # Run the graph
        result = graph.invoke(initial_state)
        
        # Extract assistant's response
        assistant_message = result["messages"][-1]
        
        return jsonify({
            "response": assistant_message.content,
            "status": "success"
        })
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})

@app.route('/')
def index():
    """Root endpoint."""
    return jsonify({
        "message": "AI-Native Commerce Platform API",
        "version": "0.1.0",
        "status": "running"
    })

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv("FLASK_DEBUG", "False").lower() == "true")
