# AI-Native Commerce Platform

An AI-powered e-commerce platform with conversational search capabilities, built with React, TypeScript, and Flask.

## 🚀 Quick Start

Get the entire application running with a single command:

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-native-commerce-platform.git
cd ai-native-commerce-platform

# Create .env file (copy from example and update with your API keys)
cp .env.example .env

# Start all services
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:80
- Backend API: http://localhost:5000
- ChromaDB: http://localhost:8000

## 🏗️ Architecture

The platform consists of three main components:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│  ChromaDB   │
│  React/TS   │◀────│    Flask    │◀────│Vector Store │
└─────────────┘     └─────────────┘     └─────────────┘
                          │
                          ▼
                    ┌─────────────┐
                    │  LangChain  │
                    │    & LLM    │
                    └─────────────┘
```

- **Frontend**: React application with TypeScript, Zustand for state management, and Tailwind CSS for styling
- **Backend**: Flask API with LangChain and Lang-graph for conversational AI
- **ChromaDB**: Vector database for storing and retrieving product embeddings
- **LLM Integration**: OpenAI API and Google Gemini for natural language understanding and generation

## 📁 Project Structure

```
ai-native-commerce-platform/
├── frontend/                # React TypeScript frontend
│   ├── src/                 # Source code
│   │   ├── api/             # API integration layer
│   │   ├── components/      # UI components
│   │   ├── store/           # Zustand state management
│   │   ├── types/           # TypeScript type definitions
│   │   └── utils/           # Utility functions
│   ├── public/              # Static assets
│   ├── Dockerfile           # Frontend Docker configuration
│   └── nginx.conf           # Nginx configuration for Docker
├── backend/                 # Flask Python backend
│   ├── app.py               # Main Flask application
│   ├── chat/                # Chat functionality
│   │   ├── graph.py         # Lang-graph implementation
│   │   ├── nodes.py         # Graph nodes
│   │   └── state.py         # State management
│   ├── manager/             # Data managers
│   │   ├── product_lookup.py # Product data access
│   │   └── vector_lookup.py  # Vector store access
│   ├── prompts/             # LLM prompts
│   │   ├── intent_classification.py # Intent classification prompts
│   │   ├── response_generation.py   # Response generation prompts
│   │   └── retrieve_helper.py       # Retrieval helper prompts
│   ├── utils/               # Utility functions
│   │   ├── constants.py     # Constants and configuration
│   │   ├── error_handler.py # Error handling utilities
│   │   ├── helper_utils.py  # Helper functions
│   │   ├── tools.py         # LLM tools
│   │   └── validation.py    # Input validation
│   ├── data/                # Data files
│   │   ├── products.json    # Product data
│   │   └── chroma_db/       # ChromaDB persistence
│   ├── Dockerfile           # Backend Docker configuration
│   └── requirements.txt     # Python dependencies
├── data/                    # Data files for ingestion
│   ├── products.json        # Product data
│   ├── skincare_catalog.xlsx # Product catalog
│   ├── product_reviews.xlsx # Product reviews
│   ├── customer_support.xlsx # Customer support data
│   └── company.txt          # Company information
├── scripts/                 # Utility scripts
│   ├── ingest-excel.py      # Data ingestion script
│   ├── setup_test.py        # Setup verification script
│   └── requirements.txt     # Script dependencies
├── docker-compose.yml       # Main Docker Compose configuration
├── docker-compose.frontend.yml # Frontend-only Docker Compose
├── docker-compose.backend.yml  # Backend-only Docker Compose
├── docker-compose.dev.yml   # Development Docker Compose
├── .env                     # Environment variables
└── DECISIONS.md             # Architecture decisions
```

## 🌟 Features

### Frontend
- Conversational search interface
- Product display with hover details
- Dark mode support
- Responsive design
- Built with React, TypeScript, and Zustand

### Backend
- Flask API with endpoints for chat and product data
- Integration with Lang-graph for stateful graph processing
- Integration with LangChain and OpenAI for LLM capabilities
- Integration with ChromaDB for vector storage and retrieval

## 🛠️ Development Setup

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- OpenAI API key

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
# LLM Configuration
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key  # Optional, if using Gemini
GOOGLE_API_KEY=your_google_api_key  # Optional, if using Google APIs
GOOGLE_PROJECT_NAME=your_project_name  # Optional, if using Google APIs

# LangSmith Configuration (Optional, for debugging LangChain)
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=default
LANGSMITH_ENDPOINT=https://api.smith.langchain.com/

# Frontend Configuration
VITE_API_BASE_URL=http://localhost:5000  # Backend API URL

# ChromaDB Configuration
# CHROMA_HOST=chromadb  # Uncomment when using Docker
# CHROMA_PORT=8000      # Uncomment when using Docker

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

### Running with Docker

To run the entire application:

```bash
docker-compose up --build
```

This will start all services:
- Frontend (accessible at http://localhost:80)
- Backend API (accessible at http://localhost:5000)
- ChromaDB (accessible at http://localhost:8000)

For development or debugging individual components:

```bash
# Run only the frontend
docker-compose -f docker-compose.frontend.yml up --build

# Run only the backend
docker-compose -f docker-compose.backend.yml up --build

# Run backend with live reload for development
docker-compose -f docker-compose.dev.yml up --build
```

#### Docker Compose Configuration

The project includes several Docker Compose files for different scenarios:

- `docker-compose.yml`: Main configuration for running the complete application
- `docker-compose.frontend.yml`: Frontend-only configuration
- `docker-compose.backend.yml`: Backend-only configuration
- `docker-compose.dev.yml`: Development configuration with live reload

### Local Development

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:5173.

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The backend will be available at http://localhost:5000.

## 📊 Data Setup

The application uses ChromaDB to store vector embeddings of product data, reviews, and company information. To ingest data into ChromaDB:

```bash
# Activate your Python environment
cd scripts
python ingest-excel.py --file ../data/skincare_catalog.xlsx --doc_type product --collection evergrow_skincare_catalog

# Ingest product reviews
python ingest-excel.py --file ../data/product_reviews.xlsx --doc_type review --collection evergrow_skincare_catalog

# Ingest company information
python ingest-excel.py --file ../data/company.txt --doc_type description --collection evergrow_skincare_catalog
```

The script supports the following document types:
- `product`: Product catalog data
- `review`: Product reviews
- `ticket`: Customer support tickets
- `description`: Company or product descriptions (text files)

## 🔌 API Endpoints

### Backend API

- `GET /health`: Health check endpoint
- `POST /api/assist`: Chat endpoint for interacting with the LLM
- `GET /api/products`: Endpoint to retrieve all products

Example chat request:

```bash
curl -X POST http://localhost:5000/api/assist \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about your skincare products", "sessionId": "user1234"}'
```

## 🧪 Testing

Run the setup test script to verify your installation:

```bash
# Make sure you're in the project root directory
cd scripts

# Install required dependencies
pip install -r requirements.txt

# Run the setup test
python setup_test.py
```

This script will check:
- Environment variables configuration
- Backend health and API endpoints
- Frontend accessibility
- End-to-end functionality

If any issues are found, the script will provide guidance on how to resolve them.

## 🔄 Deployment

The application is containerized and can be deployed to any Docker-compatible environment:

1. Build the Docker images:
   ```bash
   docker-compose build
   ```

2. Push the images to a registry (optional):
   ```bash
   docker-compose push
   ```

3. Deploy to your environment:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

## 🔮 Next Steps

- Add user authentication and personalization
- Implement product recommendations based on user history
- Add payment processing integration
- Enhance the conversational capabilities with more domain knowledge
- Implement A/B testing for different LLM prompts
- Add analytics and monitoring
