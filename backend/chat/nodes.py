"""
Enhanced LangGraph node implementations using class-based architecture.
Provides better dependency management, configuration, and testability.
"""
import json
import time
from typing import Dict, Any, Optional, List, Tuple
import structlog
from langchain.chat_models import init_chat_model
from langchain.schema import Document
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser

from .state import ChatState, Product, Citation, ClassifyAndExtractUserIntent, FollowupUser, SearchQuery
from utils.constants import (
    LLMConfig, ConversationConfig, RetrievalConfig,ErrorMessages, CONSTRAINT_NATURAL_LANGUAGE_MAP
)
from utils.tools import ToolManager
from manager.vector_lookup import VectorStoreManager
from manager.product_lookup import ProductLookupManager
from prompts.intent_classification import IntentClassificationPrompts
from prompts.followup_generation import FollowupPrompts
from prompts.response_generation import ResponsePrompts
from prompts.retrieve_helper import RetrievePrompt

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
            model=LLMConfig.GPT_4_O_MINI_MODEL,
            model_provider="openai",
            temperature=LLMConfig.CLASSIFICATION_TEMPERATURE,
            max_tokens=LLMConfig.MAX_TOKENS_CLASSIFICATION
        )
        
        # Bind tools for intent classification
        self.gpt_3_5 = ToolManager.bind_classification_tools(base_gpt_3_5)

        self.classifier_gpt = base_gpt_3_5.with_structured_output(schema=ClassifyAndExtractUserIntent)
        self.followup_gpt = base_gpt_3_5.with_structured_output(schema=FollowupUser)
        
        self.gemini_flash = init_chat_model(
            model=LLMConfig.GEMINI_2_0_FLASH_MODEL,
            model_provider="google-genai", 
            temperature=LLMConfig.GENERATION_TEMPERATURE
        )

        self.retrieve_gemini = self.gemini_flash.with_structured_output(schema=SearchQuery)
        
        # Initialize dependencies
        self.vector_store_manager = vector_store_manager or VectorStoreManager()
        self.product_lookup_manager = product_lookup_manager or ProductLookupManager()
        
        # Initialize prompt managers
        self.intent_prompts = IntentClassificationPrompts()
        self.followup_prompts = FollowupPrompts()
        self.response_prompts = ResponsePrompts()
        self.retrieve_prompt = RetrievePrompt()
        
        logger.info("conversation_orchestrator_initialized",
                   gpt_model=LLMConfig.GPT_4_O_MINI_MODEL,
                   gemini_model=LLMConfig.GEMINI_2_0_FLASH_MODEL)
    
    def entry_node(self, state: ChatState) -> Dict[str, Any]:
        """
        Entry point for each conversation turn.
        Increments turn count and validates input.
        """
        # Return only fields that need updating
        return {
            "turn_count": state.turn_count + 1,
        }
    
    def classify_intent_node(self, state: ChatState) -> Dict[str, Any]:
        """
        Classify user intent using GPT-3.5 with tool-based classification.
        Enhanced with proper tool call parsing and validation.
        """
        start_time = time.time()
        logger.info("classify_intent_start", session_id=state.session_id)
        
        try:
            # Prepare the classification prompt
            system_prompt = self.intent_prompts.get_system_prompt()
            example_messages = self.intent_prompts.get_examples()
            user_prompt = self.intent_prompts.get_classification_prompt(
                user_messages=state.user_messages,
                ai_messages=state.ai_messages
            )
            
            # Create messages for tool-bound LLM
            messages = [
                {"role": "system", "content": system_prompt},
                *example_messages,
                {"role": "user", "content": user_prompt}
            ]           

            # Parse tool calls from response
            classification_result = self.classifier_gpt.invoke(messages)

            # Debug classification result
            logger.debug("classification_result_debug",
                        session_id=state.session_id,
                        classification_result=classification_result)
            
            if classification_result:
                # Log successful classification
                latency = int((time.time() - start_time) * 1000)
                logger.info("classify_intent_success",
                           session_id=state.session_id,
                           latency_ms=latency)
                
                should_ask = "no" if state.turn_count == 3 else classification_result.ask_followup
                
                return {
                    "extracted_info": classification_result,
                    "intent": classification_result.intent,
                    "ask_followup": should_ask,
                    "followup_topics": classification_result.followup_topics
                }
            else:
                # Handle classification failure
                logger.warning("classification_fallback_applied", session_id=state.session_id)
                return self._get_fallback_intent_classification()
                
        except Exception as e:
            logger.error("classify_intent_error", 
                        session_id=state.session_id, 
                        error=str(e))
            return self._get_fallback_intent_classification()
    
    def generate_followup_node(self, state: ChatState) -> Dict[str, Any]:
        """
        Generate contextual follow-up questions using Gemini.
        Enhanced with better prompt engineering.
        """
        # Generate contextual followup question with conversation history
        followup_system_prompt = self.followup_prompts.get_system_prompt()
        followup_user_prompt = self.followup_prompts.get_followup_prompt(
            followup_topics=state.followup_topics,
            user_messages=state.user_messages,
            assistant_messages=state.ai_messages
        )

        # Create messages for tool-bound LLM
        messages = [
            {"role": "system", "content": followup_system_prompt},
            {"role": "user", "content": followup_user_prompt}
        ]
        
        followup = self.followup_gpt.invoke(messages)

        # print followup
        logger.debug("followup_generated",
                    session_id=state.session_id,
                    followup=followup)

        updated_ai_messages = state.ai_messages

        if followup:
            updated_ai_messages.append(followup.followup_question)
            
        else:
            updated_ai_messages.append("What are your major concerns?")
        
        return {
            "ai_messages": updated_ai_messages
        }
            
    
    def retrieval_node(self, state: ChatState) -> Dict[str, Any]:
        """
        Enhanced retrieval with better filtering and error handling.
        """
        start_time = time.time()
        logger.info("retrieval_start", session_id=state.session_id)
        
        try:
            
            system_prompt = self.retrieve_prompt.get_system_prompt()
            example_messages = self.retrieve_prompt.get_messages_examples()
            user_prompt = self.retrieve_prompt.get_user_prompt(
                state.user_messages, state.ai_messages, state.extracted_info)
            
            messages = [
                {"role": "system", "content": system_prompt},
                *example_messages,
                {"role": "user", "content": user_prompt}
            ]

            search_query = self.retrieve_gemini.invoke(messages)

            # print search query
            logger.debug("search_query_debug",
                        session_id=state.session_id,
                        search_query=search_query)
            
            query = search_query.query
            metadata_filters = search_query.metadata_filters

            should_apply_filters = True if state.intent in ["RECOMMEND_SPECIFIC", "RECOMMEND_VAGUE"] else False

            retrieved_docs = self.vector_store_manager.similarity_search(
                query=query,
                k=RetrievalConfig.DEFAULT_SIMILARITY_K,
                # Do not apply filters for informational query
                filter=metadata_filters if should_apply_filters else None,
                score_threshold=RetrievalConfig.SIMILARITY_SCORE
            )
            
            # Log retrieval results
            latency = int((time.time() - start_time) * 1000)
            logger.info("retrieval_success",
                       session_id=state.session_id,
                       documents_retrieved=len(retrieved_docs),
                       filter=metadata_filters,
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
        try:
            # Extract and validate products from documents
            product_candidates = self._extract_products_from_docs(state.retrieved_docs)
            
            
            # Rank by margin with similarity tie-breaking
            ranked_products = self._rank_products_by_margin(
                products=product_candidates,
                retrieved_docs=state.retrieved_docs
            )
            
            final_products = ranked_products[:RetrievalConfig.TOP_PRODUCTS_FOR_RECOMMENDATION]
            
            
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
        
        try:
            if state.intent in ["INFO_GENERAL", "INFO_PRODUCT", "OTHER"]:
                ai_message, citations, products = self._generate_informational_response_data(state)
            else:
                ai_message, citations, products = self._generate_recommendation_response_data(state)
            
            ai_messages = state.ai_messages
            ai_messages.append(ai_message)

            return {
                "ai_messages": ai_messages,
                "citations": citations,
                "products": products
            }
            
        except Exception as e:
            logger.error("generate_ui_error", 
                        session_id=state.session_id, 
                        error=str(e))
            return {
                "ai_messages": [ErrorMessages.GENERATION_ERROR],
                "citations": []
            }
    
    # Private helper methods

    # def _parse_tool_calls(self, response) -> Optional[Dict[str, Any]]:
    #     # log response
    #     logger.info("response_debug", response=response)

    #     if not hasattr(response, 'tool_calls') or not response.tool_calls:
    #         logger.warning("no_tool_calls_found", 
    #                 has_attr=hasattr(response, 'tool_calls'),
    #                 is_empty=not response.tool_calls if hasattr(response, 'tool_calls') else True)
    #         return None
            
    #         # Get the first tool call
    #     tool_call = response.tool_calls[0]

    #     return tool_call.get('args', {})

    
    # def _parse_intent_tool_calls(self, response) -> Optional[Dict[str, Any]]:
    #     """
    #     Parse and validate tool calls from LLM response.
    #     Simplified for direct Dict return from tool.
    #     """
    #     try:
    #         # Check if response has tool_calls attribute and it's not empty
    #         if not hasattr(response, 'tool_calls') or not response.tool_calls:
    #             logger.warning("no_tool_calls_found", 
    #                           has_attr=hasattr(response, 'tool_calls'),
    #                           is_empty=not response.tool_calls if hasattr(response, 'tool_calls') else True)
    #             return None
            
    #         # Get the first tool call
    #         tool_call = response.tool_calls[0]
            
    #         # Validate it's the classify_user_intent tool
    #         if tool_call.get('name') != 'classify_user_intent':
    #             logger.warning("unexpected_tool_call", tool_name=tool_call.get('name'))
    #             return None
            
    #         # Extract arguments from the tool call - these are the direct function parameters
    #         args = tool_call.get('args', {})
            
    #         if not args:
    #             logger.warning("empty_tool_args")
    #             return None
            
    #         # print args
    #         logger.debug("tool_args", args=args)

    #         # Only add keys that exist in args
    #         detected_constraints = {}
    #         constraint_keys = ["category", "skin_concern", "avoid_ingredients", 
    #                           "desired_ingredients", "price_cap", "target_sku", "finish"]
            
    #         for key in constraint_keys:
    #             if key in args and args[key] is not None:
    #                 detected_constraints[key] = args[key]

    #         # The tool now returns a Dict directly, so we can use the args as-is
    #         # The tool handles all the business logic internally
    #         result = {
    #             "intent": args.get("intent"),
    #             "ask_followup": args.get("ask_followup", False),
    #             "constraints": detected_constraints,
    #             "followup_question": args.get("followup_question"),
    #             "confidence_score": args.get("confidence_score")
    #         }
            
    #         return result
            
    #     except Exception as e:
    #         logger.error("tool_call_parse_error", 
    #                     error=str(e),
    #                     error_type=type(e).__name__)
    #         return None

    # def _determine_followup_strategy_static(
    #     self, 
    #     turn_count: int, 
    #     constraints: Dict[str, Any], 
    #     missing_keys: List[str]
    # ) -> Tuple[bool, List[str]]:
    #     """Enhanced followup strategy with smarter decision making (static version for update pattern)."""
    #     # Never ask after max turns
    #     if turn_count >= ConversationConfig.MAX_TURNS:
    #         return False, []
        
    #     followup_keys = []
        
    #     # Check critical constraints first
    #     for constraint in ConversationConfig.CRITICAL_CONSTRAINTS:
    #         if constraint in missing_keys:
    #             followup_keys.append(constraint)
        
    #     # If we have critical constraints to ask about, return them
    #     if followup_keys:
    #         return True, followup_keys
        
    #     # Check important constraints on early turns
    #     if turn_count < ConversationConfig.MAX_FOLLOWUP_TURNS:
    #         for constraint in ConversationConfig.IMPORTANT_CONSTRAINTS:
    #             if constraint in missing_keys:
    #                 followup_keys.append(constraint)
        
    #     # If we have important constraints to ask about, return them
    #     if followup_keys:
    #         return True, followup_keys
        
    #     # Check if we have minimum info for good recommendations
    #     if (turn_count == 0 and 
    #         len(constraints) < ConversationConfig.MIN_CONSTRAINTS_FOR_RECOMMENDATION):
    #         for constraint in ConversationConfig.NICE_TO_HAVE_CONSTRAINTS:
    #             if constraint in missing_keys:
    #                 followup_keys.append(constraint)
        
    #     return len(followup_keys) > 0, followup_keys
    
    # def _build_retrieval_filter(self, constraints: Dict[str, Any]) -> Dict[str, Any]:
    #     """Build optimized filter dictionary for vector search."""
    #     filter_dict = {}
        
    #     # Add category filter if present
    #     if 'category' in constraints and constraints['category']:
    #         filter_dict['category'] = constraints['category']
        
    #     # Add other relevant filters based on metadata structure
    #     # This would depend on how your vector store is set up
        
    #     return filter_dict
    
    def _get_fallback_intent_classification(self) -> Dict[str, Any]:
        """Fallback intent classification in case of error."""
        fallback_intent = ClassifyAndExtractUserIntent(
            intent="RECOMMEND_VAGUE",
            ask_followup="yes",
            followup_topics=[
                'category',
                'concerns'
            ]
        )
        return {
            "intent": "RECOMMEND_VAGUE",
            "ask_followup": "yes",
            "followup_topics": [
                'category',
                'concerns'
            ],
            "extracted_info": fallback_intent
        }
    
    def _extract_products_from_docs(self, docs: List[Document]) -> List[Product]:
        """Extract and validate products from retrieved documents."""
        products = []
        for doc in docs:
            product_id = doc.metadata.get('product_id')
            if product_id:
                product = self.product_lookup_manager.get_product_by_id(product_id)
                if product:
                    products.append(product)
        logger.info("extracted_products", products=products)
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
            return ErrorMessages.NO_PRODUCTS_FOUND, [], []
        
        # Generate recommendation using enhanced prompt with conversation history
        system_prompt = self.response_prompts.get_recommendation_system_prompt()
        examples = self.response_prompts.get_recommendation_examples()
        user_prompt = self.response_prompts.get_user_recommendation_prompt(
            user_messages=state.user_messages,
            ai_messages=state.ai_messages,
            products=top_products
        )

        # log examples

        messages = [
                {"role": "system", "content": system_prompt},
                *examples,
                {"role": "user", "content": user_prompt}
            ]

        # log messages
        logger.info("test_messages", messages=messages) 
        
        response = self.gemini_flash.invoke(messages)
        
        return response.content.strip(), [], state.products
    
    def _generate_informational_response_data(self, state: ChatState) -> Tuple[str, List[Citation]]:
        """Generate informational answer with citations (returns data for update pattern)."""

        logger.info("generate_informational_response_data", state=state)

        if not state.retrieved_docs:
            return "I couldn't find relevant information to answer your question. By the way do you want me to recommend any products", [], []
        
        # Prepare context snippets
        snippets = []
        products = []
        for i, doc in enumerate(state.retrieved_docs):
            doc_type = doc.metadata.get('doc_type')
            if doc_type == 'product':
                product_id = doc.metadata.get('product_id')
                product = self.product_lookup_manager.get_product_by_id(product_id)
                if product:
                    products.append(product)
                    continue
            content = doc.page_content
            snippet_text = doc.page_content
            if len(snippet_text) > RetrievalConfig.MAX_SNIPPET_LENGTH:
                snippet_text = snippet_text[:RetrievalConfig.MAX_SNIPPET_LENGTH] + "..."
            
            snippets.append({
                "id": doc.id,
                "content": content,
                "snippet": snippet_text,
                "source": doc.metadata.get('source', 'Product Information')
            })
            if len(snippets) >= RetrievalConfig.MAX_CITATIONS:
                break
        
        ranked_products = self._rank_products_by_margin(products, state.retrieved_docs)
        
        logger.info("context_snippets", context_snippets=snippets)

        # Generate informational response with conversation history
        system_prompt = self.response_prompts.get_informational_system_prompt()
        examples = self.response_prompts.get_informational_examples()
        user_prompt = self.response_prompts.get_informational_prompt(
            context_snippets=snippets,
            user_messages=state.user_messages,
            ai_messages=state.ai_messages
        )

        messages = [
                {"role": "system", "content": system_prompt},
                *examples,
                {"role": "user", "content": user_prompt}
            ]
        
        # log messages
        logger.info("test_messages", messages=messages)
        
        response = self.gemini_flash.invoke(messages)

        logger.info("generate_response", response=response)
        
        # Create citations
        citations = [
            Citation(id=snippet["id"], snippet=snippet["snippet"])
            for snippet in snippets
        ]
        
        return response.content.strip(), citations, ranked_products


# Create global instance for use in graph
# This can be initialized once and reused across requests
orchestrator = ConversationOrchestrator()

# Export node functions for LangGraph compatibility (Update Pattern)
def entry_node(state: ChatState) -> Dict[str, Any]:
    return orchestrator.entry_node(state)

def classify_intent_node(state: ChatState) -> Dict[str, Any]:
    return orchestrator.classify_intent_node(state)

def generate_followup_node(state: ChatState) -> Dict[str, Any]:
    return orchestrator.generate_followup_node(state)

def retrieval_node(state: ChatState) -> Dict[str, Any]:
    return orchestrator.retrieval_node(state)

def rank_products_node(state: ChatState) -> Dict[str, Any]:
    return orchestrator.rank_products_node(state)

def generate_ui_node(state: ChatState) -> Dict[str, Any]:
    return orchestrator.generate_ui_node(state)