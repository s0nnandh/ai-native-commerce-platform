# AI-Native Commerce Platform Backend

This is the backend service for the AI-Native Commerce Platform. It provides a Flask API that serves a frontend with a Lang-graph stateful graph and interacts with LLMs and Chroma to serve API requests.

## Project Structure

```
backend/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
├── requirements.txt       # Python dependencies
├── .env.example           # Example environment variables
├── scripts/               # Utility scripts
└── utils/                 # Utility modules
    ├── vector_store.py    # ChromaDB vector store utilities
    └── graph_manager.py   # Lang-graph stateful graph utilities
```

## Features

- Flask API with endpoints for chat and health checks
- Integration with Lang-graph for stateful graph processing
- Integration with LangChain and OpenAI for LLM capabilities
- Integration with ChromaDB for vector storage and retrieval
- Dockerized for easy deployment

## Getting Started

### Prerequisites

- Docker and Docker Compose
- OpenAI API key

### Setup

1. Clone the repository
2. Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

3. Edit the `.env` file and add your OpenAI API key:

```
OPENAI_API_KEY=your-api-key-here
```

### Running with Docker

Build and start the Docker containers:

```bash
docker-compose up --build
```

The API will be available at http://localhost:5000.

### API Endpoints

- `GET /`: Root endpoint, returns basic API information
- `GET /api/health`: Health check endpoint
- `POST /api/chat`: Chat endpoint for interacting with the LLM

Example chat request:

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about your product catalog"}'
```

## Development

### Running Locally

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the Flask application:

```bash
python app.py
```

## Vector Store

The backend uses ChromaDB as a vector store for storing and retrieving embeddings. The `VectorStore` class in `utils/vector_store.py` provides a simple interface for interacting with ChromaDB.

## Lang-graph Integration

The backend uses Lang-graph for stateful graph processing. The `GraphManager` class in `utils/graph_manager.py` provides utilities for creating and running Lang-graph graphs.
