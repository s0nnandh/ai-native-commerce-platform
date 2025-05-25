import os
from typing import Dict, Any, List, Callable
from langgraph.graph import StateGraph
from langgraph.graph.message import MessageState
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import logging

# Configure logging
logger = logging.getLogger(__name__)

class GraphManager:
    """Manager for Lang-graph stateful graphs."""
    
    def __init__(self, llm=None):
        """Initialize the graph manager.
        
        Args:
            llm: Optional LLM instance to use
        """
        self.llm = llm or ChatOpenAI(
            model=os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo"),
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.graph = None
    
    def create_basic_rag_graph(self, retriever_func: Callable) -> StateGraph:
        """Create a basic RAG graph with retrieval, enhancement, and generation.
        
        Args:
            retriever_func: Function to retrieve context from a vector store
            
        Returns:
            Compiled StateGraph
        """
        def retrieve_context(state: Dict[str, Any]) -> Dict[str, Any]:
            """Retrieve relevant context from the vector store."""
            messages = state["messages"]
            query = messages[-1].content
            
            # Use the provided retriever function
            results = retriever_func(query)
            
            # Add context to the state
            return {
                "messages": messages,
                "context": results
            }
        
        def enhance_prompt(state: Dict[str, Any]) -> Dict[str, Any]:
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
            enhanced_message = HumanMessage(content=enhanced_content)
            
            return {"messages": messages[:-1] + [enhanced_message]}
        
        def generate_response(state: Dict[str, Any]) -> Dict[str, Any]:
            """Generate a response using the LLM."""
            messages = state["messages"]
            response = self.llm.invoke(messages)
            return {"messages": messages + [response]}
        
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
        self.graph = builder.compile()
        return self.graph
    
    def create_conversational_graph(self) -> StateGraph:
        """Create a simple conversational graph.
        
        Returns:
            Compiled StateGraph
        """
        def generate_response(state: Dict[str, Any]) -> Dict[str, Any]:
            """Generate a response using the LLM."""
            messages = state["messages"]
            response = self.llm.invoke(messages)
            return {"messages": messages + [response]}
        
        # Define the graph
        builder = StateGraph(MessageState)
        
        # Add node
        builder.add_node("generate_response", generate_response)
        
        # Set entry point
        builder.set_entry_point("generate_response")
        
        # Compile the graph
        self.graph = builder.compile()
        return self.graph
    
    def run_graph(self, user_message: str, history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run the graph with a user message.
        
        Args:
            user_message: User message text
            history: Optional conversation history
            
        Returns:
            Result state from the graph
        """
        if not self.graph:
            raise ValueError("Graph not created. Call create_basic_rag_graph or create_conversational_graph first.")
        
        # Convert history to messages if provided
        messages = []
        if history:
            for item in history:
                if item.get("role") == "user":
                    messages.append(HumanMessage(content=item.get("content", "")))
                elif item.get("role") == "assistant":
                    messages.append(AIMessage(content=item.get("content", "")))
        
        # Add current user message
        messages.append(HumanMessage(content=user_message))
        
        # Initialize state with messages
        initial_state = {"messages": messages}
        
        # Run the graph
        try:
            result = self.graph.invoke(initial_state)
            return result
        except Exception as e:
            logger.error(f"Error running graph: {str(e)}")
            raise
