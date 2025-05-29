import structlog
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .state import ChatState
from .nodes import (
    entry_node,
    classify_intent_node, 
    generate_followup_node,
    retrieval_node,
    rank_products_node,
    generate_ui_node
)
import time

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
        # workflow.add_node("evaluate_constraints", evaluate_constraints_node)
        workflow.add_node("generate_followup", generate_followup_node)
        workflow.add_node("wait_for_user", self._wait_for_user_input)  # Interrupt node
        workflow.add_node("retrieval", retrieval_node)
        workflow.add_node("rank_products", rank_products_node)
        workflow.add_node("generate_ui", generate_ui_node)
        
        # Set entry point
        workflow.set_entry_point("entry")
        
        # Define the conversation flow
        self._add_conversation_edges(workflow)
        
        # Compile graph with checkpointer and interrupt capability
        compiled_graph = workflow.compile(
            checkpointer=self.checkpointer,
            interrupt_before=["wait_for_user"]  # Interrupt before waiting for user
        )
        
        logger.info("conversation_graph_compiled", 
                   nodes_count=len(workflow.nodes),
                   edges_count=len(workflow.edges))
        
        return compiled_graph
    
    def _add_conversation_edges(self, workflow: StateGraph):
        """
        Add edges for BUSINESS-FOCUSED conversation flow with interrupts.
        
        Flow:
        1. Entry → Classify → Evaluate
        2. Branch based on business intent:
           - RECOMMEND_SPECIFIC/VAGUE + no followup → Retrieval → Recommend
           - RECOMMEND_VAGUE + followup needed → Generate Followup → INTERRUPT
           - INFO_PRODUCT → Retrieval → Answer
           - INFO_GENERAL/OTHER → Generate UI (handle directly)
        """
        
        # Sequential flow: Entry → Classification → Evaluation
        workflow.add_edge("entry", "classify_intent")
        # workflow.add_edge("classify_intent", "evaluate_constraints")
        
        # BUSINESS-FOCUSED conditional branching
        workflow.add_conditional_edges(
            "classify_intent",
            self._route_business_flow,
            {
                "followup_needed": "generate_followup",
                "recommend": "retrieval", 
                "informational": "retrieval",
                "direct_answer": "generate_ui"  # For OVERVIEW/OTHER
            }
        )
        
        # INTERRUPT FLOW: Followup → Wait for User → INTERRUPT
        workflow.add_edge("generate_followup", "wait_for_user")
        # workflow.add_edge("wait_for_user", END)  # This creates the interrupt
        
        # Recommendation flow: Retrieval → Rank → Generate
        workflow.add_conditional_edges(
            "retrieval",
            self._route_after_retrieval,
            {
                "informational": "generate_ui",      # Direct answer for questions
                "recommendation": "rank_products"    # Product ranking for shopping
            }
        )
        
        # Final steps
        workflow.add_edge("rank_products", "generate_ui")
        workflow.add_edge("generate_ui", END)
    
    def _wait_for_user_input(self, state: ChatState) -> Dict[str, Any]:
        """
        Interrupt node - triggers graph pause to wait for user input.
        This preserves all conversation context.
        """
        logger.info("waiting_for_user_input", 
                   session_id=state.session_id,
                   turn_count=state.turn_count,
                   last_ai_message=state.ai_message)
        
        # The interrupt happens automatically due to interrupt_before=["wait_for_user"]
        # This function just logs and returns empty update
        return {}
    
    def _route_business_flow(self, state: ChatState) -> Literal["followup_needed", "recommend", "informational", "direct_answer"]:
        """
        BUSINESS-FOCUSED routing based on intent and followup needs.
        """
        # Check if followup is needed (highest priority) - now applies to all intents
        if state.ask_followup == "yes":
            return "followup_needed"
        
        # Route based on business intent
        if state.intent in ["RECOMMEND_SPECIFIC", "RECOMMEND_VAGUE"]:
            return "recommend"
        elif state.intent in ["INFO_GENERAL", "INFO_PRODUCT"]:
            return "informational"
        elif state.intent in ["OTHER"]:
            return "direct_answer"
        else:
            # Default to recommendation for unknown intents
            return "recommend"
    
    def _route_after_retrieval(self, state: ChatState) -> Literal["informational", "recommendation"]:
        """
        Route after retrieval based on business intent.
        """
        logger.info("routing_after_retrieval",
                   session_id=state.session_id, 
                   intent=state.intent,
                   documents_retrieved=len(state.retrieved_docs))
        
        if state.intent in ["INFO_GENERAL", "INFO_PRODUCT"]:
            return "informational"
        else:
            return "recommendation"
    
    # Remove async methods - keep only sync + streaming-ready methods
    
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
            current_state = self.get_conversation_history(session_id, user_message)
            
            # Process through the graph (synchronous)
            result = self.graph.invoke(
                current_state,
                config=thread_config
            )

            result = ChatState(**result)
            
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
    
    def get_conversation_history(self, session_id: str, new_user_message: str) -> Dict[str, Any]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary containing conversation history
        """
        try:
            thread_config = {"configurable": {"thread_id": session_id}}
            # checkpoint = self.checkpointer.get(thread_config)

            previous_state = ChatState(
                session_id=session_id,
                turn_count=0,
                user_messages=[],
                ai_messages=[]
            )
            for state in self.graph.get_state_history(thread_config):
                logger.info("get_history_state", next=state.next)
                if not state.next:
                    break
                previous_state = ChatState(**state.values)
                break
            previous_state.user_messages.append(new_user_message)
            # logger.info("get_history_success",
            #            session_id=session_id,
            #            previous_state=previous_state)
            
            return previous_state
        except Exception as e:
            logger.error("get_history_error", 
                        session_id=session_id,
                        error=str(e))
        
        return {"session_id": session_id, "turn_count": 0}


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
        "text": "" if not state.ai_messages else state.ai_messages[-1],
        "ask_followup": state.ask_followup,
        "followup_topics": state.followup_topics,
        "products": [
            {
                "product_id": p.product_id,
                "name": p.name,
                "price_usd": p.price_usd,
                "margin_percent": p.margin_percent,
                "category": p.category,
                "top_ingredients": p.top_ingredients,
                "description": p.description,
                "tags": p.tags
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