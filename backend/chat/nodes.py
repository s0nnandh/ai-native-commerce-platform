"""
Enhanced LangGraph node implementations using class-based architecture.
Provides better dependency management, configuration, and testability.
"""
import time
from typing import Dict, Any, Optional, List, Tuple
import structlog
from langchain.chat_models import init_chat_model
from langchain.schema import Document

from .state import ChatState, Product, Citation, ClassifyAndExtractUserIntent, FollowupUser, SearchQuery
from utils.constants import (
    LLMConfig, RetrievalConfig,ErrorMessages
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
            # logger.debug("classification_result_debug",
            #             session_id=state.session_id,
            #             classification_result=classification_result)
                        
            should_ask = "no" if state.turn_count == 3 else classification_result.ask_followup
            
            return {
                "extracted_info": classification_result,
                "intent": classification_result.intent,
                "ask_followup": should_ask,
                "followup_topics": classification_result.followup_topics
            }   
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
        try:
            followup_system_prompt = self.followup_prompts.get_system_prompt()
            examples = self.followup_prompts.get_examples()
            followup_user_prompt = self.followup_prompts.get_followup_prompt(
                followup_topics=state.followup_topics,
                user_messages=state.user_messages,
                assistant_messages=state.ai_messages
            )

            # Create messages for tool-bound LLM
            messages = [
                {"role": "system", "content": followup_system_prompt},
                *examples,
                {"role": "user", "content": followup_user_prompt}
            ]
            
            followup = self.followup_gpt.invoke(messages)

            # print followup
            # logger.debug("followup_generated",
            #             session_id=state.session_id,
            #             followup=followup)

            updated_ai_messages = state.ai_messages

            if followup:
                updated_ai_messages.append(followup.followup_question)
                
            else:
                updated_ai_messages.append("What are your major concerns?")
            
            return {
                "ai_messages": updated_ai_messages
            }
        except Exception as e:
            logger.error("generate_followup_error",
                        session_id=state.session_id,
                        error=str(e))
            return {"ai_messages": ErrorMessages.NO_PRODUCTS_FOUND}
            
    
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
            # logger.debug("search_query_debug",
            #             session_id=state.session_id,
            #             search_query=search_query)
            
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
            
            filtered_products = self._apply_manual_filters(
                products=product_candidates,
                extracted_info=state.extracted_info
            )
            
            # Rank by margin with similarity tie-breaking
            ranked_products = self._rank_products_by_margin(
                products=filtered_products,
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
        # logger.info("extracted_products", products=products)
        return products
    
    def _apply_manual_filters(self, 
                              products: List[Product], 
                              extracted_info: ClassifyAndExtractUserIntent):
        return self.product_lookup_manager.filter_products_by_constraints(
            products=products,
            keywords=extracted_info.keywords,
            concerns=extracted_info.concerns,
            top_ingredients=extracted_info.top_ingredients,
            avoid_ingredients=extracted_info.avoid_ingredients,
        )


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
        # logger.info("test_messages", messages=messages) 
        
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
        
        filtered_products = self._apply_manual_filters(
            products=products,
            extracted_info=state.extracted_info
        )
        ranked_products = self._rank_products_by_margin(filtered_products, state.retrieved_docs)
        
        # logger.info("context_snippets", context_snippets=snippets)

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
        # logger.info("test_messages", messages=messages)
        
        response = self.gemini_flash.invoke(messages)

        # logger.info("generate_response", response=response)
        
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