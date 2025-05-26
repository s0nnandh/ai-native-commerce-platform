"""
Enhanced LangGraph node implementations using class-based architecture.
Provides better dependency management, configuration, and testability.
"""
import json
import time
from typing import Dict, Any, Optional, List, Tuple
import structlog
from langchain import init_chat_model
from langchain.schema import Document
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser

from .state import ChatState, IntentClassificationResult, Product, Citation
from utils.constants import (
    LLMConfig, ConversationConfig, RetrievalConfig, ResponseConfig,
    IntentConfig, ErrorMessages, CONSTRAINT_NATURAL_LANGUAGE_MAP
)
from utils.tools import ToolManager
from manager.vector_lookup import VectorStoreManager
from manager.product_lookup import ProductLookupManager
from prompts.intent_classification import IntentClassificationPrompts
from prompts.followup_generation import FollowupPrompts
from prompts.response_generation import ResponsePrompts

logger = structlog.get_logger()


class ConversationOrchestrator:
    """
    Main orchestrator class for conversation nodes.
    Manages LLM clients, dependencies, and provides node functions for LangGraph.
    """
    
    def __init__(
        self,
        vector_store_manager: Optional[VectorStoreManager] = None,
        product_lookup_manager: Optional[ProductLookupManager] = None
    ):
        """Initialize the orchestrator with LLM clients and dependencies."""
        
        # Initialize LLM clients using init_chat_model with tool binding
        base_gpt_3_5 = init_chat_model(
            model=LLMConfig.GPT_3_5_MODEL,
            model_provider="openai",
            temperature=LLMConfig.CLASSIFICATION_TEMPERATURE,
            max_tokens=LLMConfig.MAX_TOKENS_CLASSIFICATION
        )
        
        # Bind tools for intent classification
        self.gpt_3_5 = ToolManager.bind_classification_tools(base_gpt_3_5)
        
        self.gemini_flash = init_chat_model(
            model=LLMConfig.GEMINI_FLASH_MODEL,
            model_provider="google-genai", 
            temperature=LLMConfig.GENERATION_TEMPERATURE
        )
        
        # Initialize dependencies
        self.vector_store_manager = vector_store_manager or VectorStoreManager()
        self.product_lookup_manager = product_lookup_manager or ProductLookupManager()
        
        # Initialize prompt managers
        self.intent_prompts = IntentClassificationPrompts()
        self.followup_prompts = FollowupPrompts()
        self.response_prompts = ResponsePrompts()
        
        logger.info("conversation_orchestrator_initialized",
                   gpt_model=LLMConfig.GPT_3_5_MODEL,
                   gemini_model=LLMConfig.GEMINI_FLASH_MODEL)
    
    def entry_node(self, state: ChatState) -> Dict[str, Any]:
        """
        Entry point for each conversation turn.
        Increments turn count and validates input.
        """
        start_time = time.time()
        logger.info("entry_node_start", 
                   session_id=state.session_id, 
                   current_turn=state.turn_count)
        
        # Validate user message
        user_message = state.user_message or ""
        if not user_message.strip():
            logger.warning("entry_node_empty_message", session_id=state.session_id)
            user_message = ""
        
        # Log entry completion
        latency = int((time.time() - start_time) * 1000)
        logger.info("entry_node_complete", 
                   session_id=state.session_id,
                   turn=state.turn_count + 1,
                   message_length=len(user_message),
                   latency_ms=latency)
        
        # Return only fields that need updating
        return {
            "turn_count": state.turn_count + 1,
            "user_message": user_message
        }
    
    def classify_intent_node(self, state: ChatState) -> Dict[str, Any]:
        """
        Classify user intent using GPT-3.5 with modern tool binding.
        Enhanced with better error handling and validation.
        """
        start_time = time.time()
        logger.info("classify_intent_start", session_id=state.session_id)
        
        try:
            # Prepare the classification prompt
            system_prompt = self.intent_prompts.get_system_prompt()
            user_message = state.user_message or ""
            
            # Create messages for tool-bound LLM
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # Invoke LLM with bound tools
            response = self.gpt_3_5.invoke(messages)
            
            # Parse tool calls from response
            classification_result = self._parse_tool_calls(response)
            
            if classification_result:
                # Extract results for state update
                intent = classification_result.get("intent")
                detected_constraints = classification_result.get("detected_constraints", {})
                
                # Merge constraints with existing ones
                merged_constraints = {**state.constraints}
                for key, value in detected_constraints.items():
                    if key in ['avoid_ingredients', 'desired_ingredients']:
                        # Merge lists, avoiding duplicates
                        existing = merged_constraints.get(key, [])
                        if isinstance(existing, list) and isinstance(value, list):
                            merged_constraints[key] = list(set(existing + value))
                        else:
                            merged_constraints[key] = value if isinstance(value, list) else [value]
                    else:
                        merged_constraints[key] = value
                
                # Log successful classification
                latency = int((time.time() - start_time) * 1000)
                logger.info("classify_intent_success",
                           session_id=state.session_id,
                           intent=intent,
                           constraints_count=len(detected_constraints),
                           confidence=classification_result.get("confidence_score"),
                           latency_ms=latency)
                
                return {
                    "intent": intent,
                    "constraints": merged_constraints
                }
            else:
                # Handle parsing failure
                logger.warning("classification_fallback_applied", session_id=state.session_id)
                return {"intent": "vague"}
                
        except Exception as e:
            logger.error("classify_intent_error", 
                        session_id=state.session_id, 
                        error=str(e))
            return {"intent": "vague"}
    
    def evaluate_constraints_node(self, state: ChatState) -> Dict[str, Any]:
        """
        Enhanced constraint evaluation with smarter followup logic.
        """
        start_time = time.time()
        logger.info("evaluate_constraints_start", session_id=state.session_id)
        
        # Calculate missing constraints
        all_constraints = ConversationConfig.CONSTRAINT_PRIORITY_ORDER
        missing_keys = [
            key for key in all_constraints
            if key not in state.constraints or not state.constraints[key]
        ]
        
        # Determine followup strategy using enhanced logic
        should_ask, followup_key = self._determine_followup_strategy_static(
            state.turn_count, state.constraints, missing_keys
        )
        
        # Log constraint evaluation
        latency = int((time.time() - start_time) * 1000)
        logger.info("evaluate_constraints_complete",
                   session_id=state.session_id,
                   total_constraints=len(state.constraints),
                   missing_constraints=len(missing_keys),
                   ask_followup=should_ask,
                   followup_key=followup_key,
                   latency_ms=latency)
        
        return {
            "missing_keys": missing_keys,
            "ask_followup": should_ask,
            "followup_key": followup_key
        }
    
    def ask_followup_node(self, state: ChatState) -> Dict[str, Any]:
        """
        Generate contextual follow-up questions using Gemini.
        Enhanced with better prompt engineering.
        """
        start_time = time.time()
        logger.info("ask_followup_start", 
                   session_id=state.session_id,
                   followup_key=state.followup_key)
        
        try:
            # Generate contextual followup question
            followup_prompt = self.followup_prompts.get_followup_prompt(
                followup_key=state.followup_key,
                user_message=state.user_message,
                existing_constraints=state.constraints,
                turn_count=state.turn_count
            )
            
            # Generate with appropriate token limit
            response = self.gemini_flash.invoke(
                [{"role": "user", "content": followup_prompt}],
                max_tokens=LLMConfig.MAX_TOKENS_FOLLOWUP
            )
            
            ai_message = response.content.strip()
            
            # Log successful generation
            latency = int((time.time() - start_time) * 1000)
            logger.info("ask_followup_success",
                       session_id=state.session_id,
                       followup_key=state.followup_key,
                       response_length=len(ai_message),
                       latency_ms=latency)
            
            return {"ai_message": ai_message}
            
        except Exception as e:
            logger.error("ask_followup_error", 
                        session_id=state.session_id, 
                        error=str(e))
            # Enhanced fallback with context
            constraint_name = CONSTRAINT_NATURAL_LANGUAGE_MAP.get(
                state.followup_key, state.followup_key
            )
            fallback_message = f"Could you tell me more about your {constraint_name}?"
            
            return {"ai_message": fallback_message}
    
    def retrieval_node(self, state: ChatState) -> Dict[str, Any]:
        """
        Enhanced retrieval with better filtering and error handling.
        """
        start_time = time.time()
        logger.info("retrieval_start", session_id=state.session_id)
        
        try:
            # Build enhanced filter from constraints
            filter_dict = self._build_retrieval_filter(state.constraints)
            
            # Perform similarity search with dynamic k based on constraints
            k_value = self._calculate_optimal_k(state.constraints)
            query = state.user_message or ""
            
            retrieved_docs = self.vector_store_manager.similarity_search(
                query=query,
                k=k_value,
                filter=filter_dict,
                score_threshold=RetrievalConfig.MIN_SIMILARITY_SCORE
            )
            
            # Log retrieval results
            latency = int((time.time() - start_time) * 1000)
            logger.info("retrieval_success",
                       session_id=state.session_id,
                       documents_retrieved=len(retrieved_docs),
                       filter_keys=list(filter_dict.keys()) if filter_dict else [],
                       k_value=k_value,
                       latency_ms=latency)
            
            return {"retrieved_docs": retrieved_docs}
            
        except Exception as e:
            logger.error("retrieval_error", 
                        session_id=state.session_id, 
                        error=str(e))
            return {"retrieved_docs": []}
    
    def rank_products_node(self, state: ChatState) -> Dict[str, Any]:
        """
        Enhanced product ranking with better constraint filtering.
        """
        start_time = time.time()
        logger.info("rank_products_start", session_id=state.session_id)
        
        try:
            # Extract and validate products from documents
            product_candidates = self._extract_products_from_docs(state.retrieved_docs)
            
            # Apply constraint-based filtering
            filtered_products = self.product_lookup_manager.filter_products_by_constraints(
                products=product_candidates,
                constraints=state.constraints
            )
            
            # Rank by margin with similarity tie-breaking
            ranked_products = self._rank_products_by_margin(
                products=filtered_products,
                retrieved_docs=state.retrieved_docs
            )
            
            final_products = ranked_products[:RetrievalConfig.TOP_PRODUCTS_FOR_RECOMMENDATION]
            
            # Log ranking results
            latency = int((time.time() - start_time) * 1000)
            logger.info("rank_products_success",
                       session_id=state.session_id,
                       candidates_found=len(product_candidates),
                       after_filtering=len(filtered_products),
                       final_products=len(final_products),
                       constraints_applied=len(state.constraints),
                       latency_ms=latency)
            
            return {"products": final_products}
            
        except Exception as e:
            logger.error("rank_products_error", 
                        session_id=state.session_id, 
                        error=str(e))
            return {"products": []}
    
    def generate_ui_node(self, state: ChatState) -> Dict[str, Any]:
        """
        Enhanced response generation with mode-specific optimization.
        """
        start_time = time.time()
        logger.info("generate_ui_start", 
                   session_id=state.session_id,
                   intent=state.intent,
                   products_count=len(state.products))
        
        try:
            if state.intent == "informational":
                ai_message, citations = self._generate_informational_response_data(state)
            else:
                ai_message, citations = self._generate_recommendation_response_data(state)
            
            # Log successful generation
            latency = int((time.time() - start_time) * 1000)
            logger.info("generate_ui_success",
                       session_id=state.session_id,
                       intent=state.intent,
                       response_length=len(ai_message),
                       citations_count=len(citations),
                       latency_ms=latency)
            
            return {
                "ai_message": ai_message,
                "citations": citations
            }
            
        except Exception as e:
            logger.error("generate_ui_error", 
                        session_id=state.session_id, 
                        error=str(e))
            return {
                "ai_message": ErrorMessages.GENERATION_ERROR,
                "citations": []
            }
    
    # Private helper methods
    
    def _parse_tool_calls(self, response) -> Optional[Dict[str, Any]]:
        """Parse and validate tool calls from LLM response."""
        try:
            # Check if response has tool calls
            if hasattr(response, 'tool_calls') and response.tool_calls:
                tool_call = response.tool_calls[0]  # Get first tool call
                
                if tool_call.name == "classify_intent_and_extract_constraints":
                    # Tool call arguments are already validated by Pydantic
                    return tool_call.args
                    
            # Check for additional_kwargs format (backward compatibility)
            elif hasattr(response, 'additional_kwargs'):
                tool_calls = response.additional_kwargs.get('tool_calls', [])
                if tool_calls:
                    tool_call = tool_calls[0]
                    function_data = tool_call.get('function', {})
                    if function_data.get('name') == 'classify_intent_and_extract_constraints':
                        return json.loads(function_data.get('arguments', '{}'))
                        
        except (json.JSONDecodeError, ValueError, AttributeError) as e:
            logger.error("tool_call_parse_error", error=str(e))
            
        return None
    
    def _handle_classification_fallback(self, state: ChatState):
        """Handle classification failures with intelligent fallback."""
        state.intent = "vague"  # Safe default
        logger.warning("classification_fallback_applied", session_id=state.session_id)
    
    def _determine_followup_strategy_static(
        self, 
        turn_count: int, 
        constraints: Dict[str, Any], 
        missing_keys: List[str]
    ) -> Tuple[bool, Optional[str]]:
        """Enhanced followup strategy with smarter decision making (static version for update pattern)."""
        # Never ask after max turns
        if turn_count >= ConversationConfig.MAX_TURNS:
            return False, None
        
        # Check critical constraints first
        for constraint in ConversationConfig.CRITICAL_CONSTRAINTS:
            if constraint in missing_keys:
                return True, constraint
        
        # Check important constraints on early turns
        if turn_count < ConversationConfig.MAX_FOLLOWUP_TURNS:
            for constraint in ConversationConfig.IMPORTANT_CONSTRAINTS:
                if constraint in missing_keys:
                    return True, constraint
        
        # Check if we have minimum info for good recommendations
        if (turn_count == 0 and 
            len(constraints) < ConversationConfig.MIN_CONSTRAINTS_FOR_RECOMMENDATION):
            for constraint in ConversationConfig.NICE_TO_HAVE_CONSTRAINTS:
                if constraint in missing_keys:
                    return True, constraint
        
        return False, None
    
    def _build_retrieval_filter(self, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Build optimized filter dictionary for vector search."""
        filter_dict = {}
        
        # Add category filter if present
        if 'category' in constraints and constraints['category']:
            filter_dict['category'] = constraints['category']
        
        # Add other relevant filters based on metadata structure
        # This would depend on how your vector store is set up
        
        return filter_dict
    
    def _calculate_optimal_k(self, constraints: Dict[str, Any]) -> int:
        """Calculate optimal k value based on constraint specificity."""
        base_k = RetrievalConfig.DEFAULT_SIMILARITY_K
        
        # Reduce k if we have specific constraints (more targeted search)
        specificity_score = len([c for c in constraints.values() if c])
        
        if specificity_score >= 3:
            return max(15, base_k // 2)
        elif specificity_score >= 2:
            return max(20, int(base_k * 0.75))
        else:
            return base_k
    
    def _extract_products_from_docs(self, docs: List[Document]) -> List[Product]:
        """Extract and validate products from retrieved documents."""
        products = []
        for doc in docs:
            product_id = doc.metadata.get('product_id')
            if product_id:
                product = self.product_lookup_manager.get_product_by_id(product_id)
                if product:
                    products.append(product)
        return products
    
    def _rank_products_by_margin(self, products: List[Product], retrieved_docs: List[Document]) -> List[Product]:
        """Rank products by margin with similarity score tie-breaking."""
        # Create mapping of product_id to similarity score
        doc_scores = {}
        for doc in retrieved_docs:
            product_id = doc.metadata.get('product_id')
            if product_id:
                doc_scores[product_id] = doc.metadata.get('score', 0.0)
        
        # Sort by margin (desc) then by similarity score (desc)
        sorted_products = sorted(
            products,
            key=lambda p: (p.margin_percent, doc_scores.get(p.product_id, 0.0)),
            reverse=True
        )
        
        return sorted_products
    
    def _generate_recommendation_response_data(self, state: ChatState) -> Tuple[str, List[Citation]]:
        """Generate product recommendation with enhanced context (returns data for update pattern)."""
        top_products = state.products[:RetrievalConfig.TOP_PRODUCTS_FOR_RECOMMENDATION]
        
        if not top_products:
            return ErrorMessages.NO_PRODUCTS_FOUND, []
        
        # Generate recommendation using enhanced prompt
        recommendation_prompt = self.response_prompts.get_recommendation_prompt(
            user_query=state.user_message,
            products=top_products,
            constraints=state.constraints,
            turn_count=state.turn_count
        )
        
        response = self.gemini_flash.invoke(
            [{"role": "user", "content": recommendation_prompt}],
            max_tokens=LLMConfig.MAX_TOKENS_RECOMMENDATION
        )
        
        return response.content.strip(), []
    
    def _generate_informational_response_data(self, state: ChatState) -> Tuple[str, List[Citation]]:
        """Generate informational answer with citations (returns data for update pattern)."""
        if not state.retrieved_docs:
            return "I couldn't find relevant information to answer your question.", []
        
        # Prepare context snippets
        context_snippets = []
        for i, doc in enumerate(state.retrieved_docs[:RetrievalConfig.MAX_CITATIONS]):
            snippet_text = doc.page_content
            if len(snippet_text) > RetrievalConfig.MAX_SNIPPET_LENGTH:
                snippet_text = snippet_text[:RetrievalConfig.MAX_SNIPPET_LENGTH] + "..."
            
            context_snippets.append({
                "id": str(i + 1),
                "content": snippet_text,
                "source": doc.metadata.get('source', 'Product Information')
            })
        
        # Generate informational response
        informational_prompt = self.response_prompts.get_informational_prompt(
            user_question=state.user_message,
            context_snippets=context_snippets
        )
        
        response = self.gemini_flash.invoke(
            [{"role": "user", "content": informational_prompt}],
            max_tokens=LLMConfig.MAX_TOKENS_INFORMATIONAL
        )
        
        # Create citations
        citations = [
            Citation(id=snippet["id"], snippet=snippet["content"])
            for snippet in context_snippets
        ]
        
        return {
            "ai_message": response.content.strip(),
            "citations": citations
        }

# Create global instance for use in graph
# This can be initialized once and reused across requests
orchestrator = ConversationOrchestrator()

# Export node functions for LangGraph compatibility (Update Pattern)
def entry_node(state: ChatState) -> Dict[str, Any]:
    return orchestrator.entry_node(state)

def classify_intent_node(state: ChatState) -> Dict[str, Any]:
    return orchestrator.classify_intent_node(state)

def evaluate_constraints_node(state: ChatState) -> Dict[str, Any]:
    return orchestrator.evaluate_constraints_node(state)

def ask_followup_node(state: ChatState) -> Dict[str, Any]:
    return orchestrator.ask_followup_node(state)

def retrieval_node(state: ChatState) -> Dict[str, Any]:
    return orchestrator.retrieval_node(state)

def rank_products_node(state: ChatState) -> Dict[str, Any]:
    return orchestrator.rank_products_node(state)

def generate_ui_node(state: ChatState) -> Dict[str, Any]:
    return orchestrator.generate_ui_node(state)