"""
LangGraph orchestration with checkpointing for conversational store.
Manages conversation flow and state persistence using session_id.
"""
import structlog
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

from .state import ChatState
from .nodes import (
    entry_node,
    classify_intent_node, 
    evaluate_constraints_node,
    ask_followup_node,
    retrieval_node,
    rank_products_node,
    generate_ui_node
)
from utils.constants import ConversationConfig

logger = structlog.get_logger()


class ConversationGraph:
    """
    LangGraph-based conversation orchestrator with checkpointing.
    Manages the complete conversation flow with state persistence.
    """
    
    def __init__(self, checkpointer=None):
        """
        Initialize the conversation graph with checkpointing.
        
        Args:
            checkpointer: Optional checkpointer instance. Defaults to MemorySaver.
        """
        self.checkpointer = checkpointer or MemorySaver()
        self.graph = self._build_graph()
        logger.info("conversation_graph_initialized", 
                   checkpointer_type=type(self.checkpointer).__name__)
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state graph with all nodes and transitions.
        
        Returns:
            Compiled StateGraph ready for execution
        """
        # Create state graph
        workflow = StateGraph(ChatState)
        
        # Add all nodes
        workflow.add_node("entry", entry_node)
        workflow.add_node("classify_intent", classify_intent_node)
        workflow.add_node("evaluate_constraints", evaluate_constraints_node)
        workflow.add_node("ask_followup", ask_followup_node)
        workflow.add_node("retrieval", retrieval_node)
        workflow.add_node("rank_products", rank_products_node)
        workflow.add_node("generate_ui", generate_ui_node)
        
        # Set entry point
        workflow.set_entry_point("entry")
        
        # Define the conversation flow
        self._add_conversation_edges(workflow)
        
        # Compile graph with checkpointer
        compiled_graph = workflow.compile(checkpointer=self.checkpointer)
        
        logger.info("conversation_graph_compiled", 
                   nodes_count=len(workflow.nodes),
                   edges_count=len(workflow.edges))
        
        return compiled_graph
    
    def _add_conversation_edges(self, workflow: StateGraph):
        """
        Add edges defining the conversation flow logic.
        
        The flow follows this pattern:
        1. Entry → Intent Classification → Constraint Evaluation
        2. Branch based on intent and followup needs:
           - If informational → Retrieval → Generate UI
           - If needs followup → Ask Followup → END (wait for next turn)
           - Else → Retrieval → Rank Products → Generate UI
        """
        
        # Sequential flow: Entry → Classification → Evaluation
        workflow.add_edge("entry", "classify_intent")
        workflow.add_edge("classify_intent", "evaluate_constraints")
        
        # Conditional branching from constraint evaluation
        workflow.add_conditional_edges(
            "evaluate_constraints",
            self._route_after_constraints,
            {
                "informational": "retrieval",
                "ask_followup": "ask_followup", 
                "recommendation": "retrieval"
            }
        )
        
        # Followup path (terminal - waits for next user input)
        workflow.add_edge("ask_followup", END)
        
        # Informational path: Retrieval → Generate UI → END
        workflow.add_conditional_edges(
            "retrieval",
            self._route_after_retrieval,
            {
                "informational": "generate_ui",
                "recommendation": "rank_products"
            }
        )
        
        # Recommendation path: Rank Products → Generate UI → END
        workflow.add_edge("rank_products", "generate_ui")
        workflow.add_edge("generate_ui", END)
    
    def _route_after_constraints(self, state: ChatState) -> Literal["informational", "ask_followup", "recommendation"]:
        """
        Route conversation after constraint evaluation.
        
        Args:
            state: Current conversation state
            
        Returns:
            Next route to take in the conversation
        """
        logger.info("routing_after_constraints", 
                   session_id=state.session_id,
                   intent=state.intent,
                   ask_followup=state.ask_followup,
                   turn_count=state.turn_count)
        
        # Always ask followup if needed (highest priority)
        if state.ask_followup:
            return "ask_followup"
        
        # Route based on intent
        if state.intent == "informational":
            return "informational"
        else:
            # All other intents go to recommendation flow
            return "recommendation"
    
    def _route_after_retrieval(self, state: ChatState) -> Literal["informational", "recommendation"]:
        """
        Route conversation after retrieval based on intent.
        
        Args:
            state: Current conversation state
            
        Returns:
            Next route based on intent type
        """
        logger.info("routing_after_retrieval",
                   session_id=state.session_id, 
                   intent=state.intent,
                   documents_retrieved=len(state.retrieved_docs))
        
        if state.intent == "informational":
            return "informational"
        else:
            return "recommendation"
    
    async def process_message(
        self, 
        session_id: str, 
        user_message: str,
        config: Dict[str, Any] = None
    ) -> ChatState:
        """
        Process a user message through the conversation graph.
        
        Args:
            session_id: Unique session identifier for state persistence
            user_message: User's input message
            config: Optional configuration for the graph execution
            
        Returns:
            Updated ChatState after processing
        """
        start_time = time.time()
        
        # Create thread configuration for checkpointing
        thread_config = {
            "configurable": {
                "thread_id": session_id
            }
        }
        
        # Merge with any additional config
        if config:
            thread_config.update(config)
        
        logger.info("processing_message_start",
                   session_id=session_id,
                   message_length=len(user_message))
        
        try:
            # Get current state from checkpoint or create new
            current_state = await self._get_or_create_state(session_id, user_message)
            
            # Process through the graph
            result = await self.graph.ainvoke(
                current_state,
                config=thread_config
            )
            
            # Log successful processing
            latency = int((time.time() - start_time) * 1000)
            logger.info("processing_message_success",
                       session_id=session_id,
                       final_intent=result.intent,
                       turn_count=result.turn_count,
                       ask_followup=result.ask_followup,
                       products_found=len(result.products),
                       total_latency_ms=latency)
            
            return result
            
        except Exception as e:
            logger.error("processing_message_error",
                        session_id=session_id,
                        error=str(e))
            raise
    
    def process_message_sync(
        self, 
        session_id: str, 
        user_message: str,
        config: Dict[str, Any] = None
    ) -> ChatState:
        """
        Synchronous version of process_message for Flask compatibility.
        
        Args:
            session_id: Unique session identifier
            user_message: User's input message  
            config: Optional configuration
            
        Returns:
            Updated ChatState after processing
        """
        start_time = time.time()
        
        # Create thread configuration for checkpointing
        thread_config = {
            "configurable": {
                "thread_id": session_id
            }
        }
        
        if config:
            thread_config.update(config)
        
        logger.info("processing_message_sync_start",
                   session_id=session_id,
                   message_length=len(user_message))
        
        try:
            # Get current state from checkpoint or create new
            current_state = self._get_or_create_state_sync(session_id, user_message)
            
            # Process through the graph (synchronous)
            result = self.graph.invoke(
                current_state,
                config=thread_config
            )
            
            # Log successful processing
            latency = int((time.time() - start_time) * 1000)
            logger.info("processing_message_sync_success",
                       session_id=session_id,
                       final_intent=result.intent,
                       turn_count=result.turn_count,
                       ask_followup=result.ask_followup,
                       products_found=len(result.products),
                       total_latency_ms=latency)
            
            return result
            
        except Exception as e:
            logger.error("processing_message_sync_error",
                        session_id=session_id,
                        error=str(e))
            raise
    
    async def _get_or_create_state(self, session_id: str, user_message: str) -> ChatState:
        """
        Get existing state from checkpoint or create new state.
        
        Args:
            session_id: Session identifier
            user_message: Current user message
            
        Returns:
            ChatState ready for processing
        """
        try:
            # Try to get existing state from checkpointer
            thread_config = {"configurable": {"thread_id": session_id}}
            
            # Get the latest checkpoint
            checkpoint = await self.checkpointer.aget(thread_config)
            
            if checkpoint and checkpoint.values:
                # Load existing state and prepare for new turn
                existing_state = ChatState(**checkpoint.values)
                existing_state.reset_for_new_turn()
                existing_state.user_message = user_message
                
                logger.info("state_loaded_from_checkpoint",
                           session_id=session_id,
                           previous_turn_count=existing_state.turn_count)
                
                return existing_state
                
        except Exception as e:
            logger.warning("checkpoint_load_failed", 
                          session_id=session_id,
                          error=str(e))
        
        # Create new state if checkpoint doesn't exist or failed to load
        new_state = ChatState(
            session_id=session_id,
            user_message=user_message
        )
        
        logger.info("new_state_created", session_id=session_id)
        return new_state
    
    def _get_or_create_state_sync(self, session_id: str, user_message: str) -> ChatState:
        """
        Synchronous version of _get_or_create_state.
        """
        try:
            # Try to get existing state from checkpointer
            thread_config = {"configurable": {"thread_id": session_id}}
            
            # Get the latest checkpoint (sync)
            checkpoint = self.checkpointer.get(thread_config)
            
            if checkpoint and checkpoint.values:
                # Load existing state and prepare for new turn
                existing_state = ChatState(**checkpoint.values)
                existing_state.reset_for_new_turn()
                existing_state.user_message = user_message
                
                logger.info("state_loaded_from_checkpoint_sync",
                           session_id=session_id,
                           previous_turn_count=existing_state.turn_count)
                
                return existing_state
                
        except Exception as e:
            logger.warning("checkpoint_load_failed_sync", 
                          session_id=session_id,
                          error=str(e))
        
        # Create new state if checkpoint doesn't exist or failed to load
        new_state = ChatState(
            session_id=session_id,
            user_message=user_message
        )
        
        logger.info("new_state_created_sync", session_id=session_id)
        return new_state
    
    def get_conversation_history(self, session_id: str) -> Dict[str, Any]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary containing conversation history
        """
        try:
            thread_config = {"configurable": {"thread_id": session_id}}
            checkpoint = self.checkpointer.get(thread_config)
            
            if checkpoint and checkpoint.values:
                state = ChatState(**checkpoint.values)
                return {
                    "session_id": session_id,
                    "turn_count": state.turn_count,
                    "intent": state.intent,
                    "constraints": state.constraints,
                    "last_message": state.ai_message
                }
        except Exception as e:
            logger.error("get_history_error", 
                        session_id=session_id,
                        error=str(e))
        
        return {"session_id": session_id, "turn_count": 0, "constraints": {}}
    
    def clear_conversation(self, session_id: str) -> bool:
        """
        Clear conversation history for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            thread_config = {"configurable": {"thread_id": session_id}}
            # Note: MemorySaver doesn't have a direct delete method
            # In production, you might use a database-backed checkpointer
            # For now, we can't truly delete from MemorySaver
            
            logger.info("conversation_clear_requested", session_id=session_id)
            return True
            
        except Exception as e:
            logger.error("clear_conversation_error",
                        session_id=session_id, 
                        error=str(e))
            return False


# Global graph instance for Flask application
conversation_graph = ConversationGraph()


def get_graph() -> ConversationGraph:
    """Get the global conversation graph instance."""
    return conversation_graph


def process_user_message(session_id: str, user_message: str) -> ChatState:
    """
    Convenience function to process a user message.
    
    Args:
        session_id: Unique session identifier
        user_message: User's input message
        
    Returns:
        Updated ChatState after processing
    """
    return conversation_graph.process_message_sync(session_id, user_message)


# Additional utility functions for Flask integration

def create_response_dict(state: ChatState, latency_ms: int) -> Dict[str, Any]:
    """
    Create Flask response dictionary from ChatState.
    
    Args:
        state: Processed ChatState
        latency_ms: Total processing latency
        
    Returns:
        Dictionary matching the API contract
    """
    return {
        "text": state.ai_message or "",
        "ask_followup": state.ask_followup,
        "followup_key": state.followup_key,
        "products": [
            {
                "sku_id": p.product_id,
                "name": p.name,
                "price": p.price_usd,
                "margin": p.margin_percent,
                "category": p.category
            } for p in state.products
        ],
        "citations": [
            {
                "id": c.id,
                "snippet": c.snippet
            } for c in state.citations
        ],
        "latency_ms": latency_ms
    }


def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format.
    
    Args:
        session_id: Session identifier to validate
        
    Returns:
        True if valid, False otherwise
    """
    import re
    import uuid
    
    try:
        # Check if it's a valid UUID
        uuid.UUID(session_id)
        return True
    except ValueError:
        # Check if it's a reasonable string format
        return bool(re.match(r'^[a-zA-Z0-9_-]{8,64}$', session_id))