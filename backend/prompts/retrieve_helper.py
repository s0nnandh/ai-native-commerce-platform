from chat.state import ClassifyAndExtractUserIntent, SearchQuery
from langchain_core.utils.function_calling import tool_example_to_messages
from utils.helper_utils import get_message_summary


class RetrievePrompt:
    
    @staticmethod
    def get_system_prompt() -> str:
        """Prompt for descriptive query string to search in product knowledge base """
        return """
You are an expert AI assistant for a skincare platform. Your task is to convert structured user constraints and intent into an search text and metadata filter for semantic search over a vector database.

### Your Responsibilities:
1. Generate a descriptive **query string** that best matches the user's intent and constraints. This will be used in a vector similarity search.
2. Output **structured metadata filters** based on the input constraints to improve precision.

You must always output the result in this schema:
{
  "query": string,
  "metadata_filters": dict[str, str | list[str]] | null
}

---

### Search Database Context:

The vector database contains 4 document types:

#### 1. **Products** (`doc_type: "product"`)
Used for retrieving product recommendations and detailed information.
Includes: name, category, ingredients, tags, price, etc.
Important: Only possible values for category filter are - `serum`, `toner`, `sunscreen`, `moisturizer`, `face-mask`, `body-wash`, `shampoo`, `conditioner`, `hair-mask`

#### 2. **Reviews** (`doc_type: "review"`)
Customer feedback on products. Contains ratings, skin_type, sentiment, age group, etc.

#### 3. **Tickets** (`doc_type: "ticket"`)
Customer support issues. Includes issue type, urgency, refund/replacement offers, etc.

#### 4. **Company Description** (`doc_type: "description"`)
Company-wide info about brand, product philosophy, and ingredient summaries.

---

### Important Filtering Rules:

- If `intent` is **RECOMMEND_SPECIFIC** or **RECOMMEND_VAGUE**, limit your search to only `doc_type = "product"` (i.e., set this in `metadata_filters`).
- If `intent` is **INFO_GENERAL**, limit your search to use `doc_type = ["ticket", "description"]` 
- For all other intents (e.g., FEEDBACK, COMPLAINT, INFO), allow searching across all document types — use `doc_type` only if explicitly mentioned or implied.

---

### Metadata Fields You Can Use in Filters:

#### For Products:
- `doc_type`: always "product"
- `product_id`: id of the product
- `name`: name of the product
- `category`: category of the product
- `top_ingredients`: ingredients in the product
- `tags`: keywords for the product
- `price_usd`: price in usd

#### For Reviews:
- `doc_type`: "review"
- `reviewer_skin_type`: reviewer skin type
- `reviewer_age`: age of reviewer
- `annotated_rating`: rating out of 5 stars

#### For Tickets:
- `doc_type`: "ticket"

#### For Company Description:
- `doc_type`: "description"

---

### Output Quality Guidelines:

- Only use **metadata filters** for constraints that map directly and unambiguously to a known field.
- **Never hallucinate** values or invent metadata keys.
- If no valid filters exist, set `metadata_filters` to `null`.
- If multiple filters apply, include all relevant fields.
- If for a single filter multiple values exist, add them all in a list
"""

    @staticmethod
    def get_messages_examples() -> list:
        """Messages for multi-shot prompting"""
        examples = [
    (
        "I’m looking for a moisturizer for dry skin, preferably under $30.",
        SearchQuery(
            query="Looking for a moisturizer for dry skin under $30.",
            metadata_filters={
                "doc_type": "product",
                "category": "moisturizer",
                "tags": ["dry"],
                "price_usd": "<30"
            }
        )
    ),
    (
        "Any anti-aging creams with retinol?",
        SearchQuery(
            query="Looking for an anti-aging cream that contains retinol.",
            metadata_filters={
                "doc_type": "product",
                "category": "cream",
                "top_ingredients": ["retinol"],
                "tags": ["antiaging"]
            }
        )
    ),
    (
        "Show me a good SPF for oily skin.",
        SearchQuery(
            query="Looking for a good SPF product suitable for oily skin.",
            metadata_filters={
                "doc_type": "product",
                "category": "SPF",
                "tags": ["oily"]
            }
        )
    ),
    (
        "I want something to help with acne and brightening.",
        SearchQuery(
            query="Looking for a skincare product that targets acne and brightening.",
            metadata_filters={
                "doc_type": "product",
                "tags": ["acne", "brightening"]
            }
        )
    ),
    (
        "Is there a serum with niacinamide for sensitive skin?",
        SearchQuery(
            query="Looking for a serum with niacinamide for sensitive skin.",
            metadata_filters={
                "doc_type": "product",
                "category": "serum",
                "top_ingredients": ["niacinamide"],
                "tags": ["sensitive"]
            }
        )
    ),
    ]
        messages = []
        for query, search_query in examples:
            messages.extend(tool_example_to_messages(query, [search_query]))
        return messages
    
    @staticmethod
    def get_user_prompt(user_messages: list[str], ai_messages: list[str], extracted_info: ClassifyAndExtractUserIntent) -> str:
        """User prompt to use extracted information to generate search query"""
        messages_summary = get_message_summary(user_messages, ai_messages)
        return f"""
### Message History
{messages_summary}

### Extracted Information
Use the following structured fields extracted from the user's message to generate a clean and relevant search query and metadata filters:

{{
  "intent": "{extracted_info.intent}",
  "type of skincare product": {extracted_info.category},
  "specific product names": {extracted_info.name},
  "preferred active ingredients": {extracted_info.top_ingredients},
  "primary concerns": {extracted_info.concerns},
  "any preferences or keywords": {extracted_info.keywords},
  "ingredients they want to avoid": {extracted_info.avoid_ingredients},
  "specific product identifiers": {extracted_info.product_id},
  "price": {extracted_info.price},
  "other": {extracted_info.other}
}}

Use these to form the best possible `query` and `metadata_filters`. Ignore fields with empty values — they are optional.
"""

