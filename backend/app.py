"""
Simple Flask app for conversational store backend.
"""
import time
import uuid
from flask import Flask, request, jsonify
import structlog
from flask_cors import CORS

# Import our components
from chat.graph import process_user_message, create_response_dict
from utils.validation import validate_assist_request, ValidationError
from utils.error_handler import handle_api_error, APIError, create_fallback_response
from manager.product_lookup import product_lookup_manager

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ]
        ),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/api/assist', methods=['POST'])
def assist():
    """Main chat endpoint."""
    start_time = time.time()
    request_id = str(uuid.uuid4())[:8]
    
    logger.info("assist_request", request_id=request_id)
    
    try:
        # Validate request
        session_id, user_message = validate_assist_request(request.get_json())
        
        # Process with LangGraph
        result_state = process_user_message(session_id, user_message)
        
        # Create response
        latency_ms = int((time.time() - start_time) * 1000)
        response = create_response_dict(result_state, latency_ms)
        
        logger.info("assist_success",
                   request_id=request_id,
                   session_id=session_id,
                   latency_ms=latency_ms)
        
        return jsonify(response), 200
        
    except (ValidationError, APIError) as e:
        return handle_api_error(e, request_id)
        
    except Exception as e:
        logger.error("assist_error", request_id=request_id, error=str(e))
        
        # Return fallback response instead of error
        fallback = create_fallback_response()
        return jsonify(fallback), 200


@app.route('/api/products', methods=['GET'])
def get_products():
    """Retrieve all products."""
    try:
        # Get all products from the product lookup manager
        products = product_lookup_manager.get_all_products()
        
        # Convert products to dictionaries
        products_data = [product.dict() for product in products]
        
        logger.info("products_retrieved", count=len(products_data))
        
        return jsonify({
            "products": products_data,
            "count": len(products_data),
            "timestamp": time.time()
        }), 200
        
    except Exception as e:
        logger.error("products_error", error=str(e))
        return jsonify({
            "error": "Failed to retrieve products",
            "message": str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time()
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({"error": "Method not allowed"}), 405


if __name__ == '__main__':
    logger.info("starting_flask_app")
    app.run(host='0.0.0.0', port=5000, debug=True)
