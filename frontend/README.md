# AI-Native Commerce Platform Frontend

This is the frontend for the AI-Native Commerce Platform, a conversational e-commerce application that allows users to discover products through natural language interactions.

## Technology Stack

- **React**: UI library for building the user interface
- **TypeScript**: For type-safe code
- **Zustand**: For state management
- **Tailwind CSS**: For styling
- **Axios**: For API requests
- **Docker**: For containerization

## Project Structure

```
frontend/
├── public/                # Static assets
├── src/
│   ├── api/              # API integration layer
│   │   ├── config.ts     # API configuration
│   │   ├── client.ts     # Axios client setup
│   │   └── assistApi.ts  # API service for the assist endpoint
│   ├── components/       # Reusable UI components
│   │   ├── common/       # Shared components
│   │   ├── layout/       # Layout components (Header, Footer)
│   │   ├── product/      # Product-related components
│   │   └── search/       # Search-related components
│   ├── hooks/            # Custom React hooks
│   ├── pages/            # Page components
│   │   └── HomePage.tsx  # Main page
│   ├── store/            # Zustand state management
│   │   ├── conversationStore.ts  # Store for conversation state
│   │   ├── productStore.ts       # Store for product state
│   │   └── uiStore.ts            # Store for UI state
│   ├── types/            # TypeScript type definitions
│   ├── utils/            # Utility functions
│   ├── App.tsx           # Main App component
│   ├── main.tsx          # Entry point
│   └── index.css         # Global styles with Tailwind
├── .dockerignore         # Docker ignore file
├── Dockerfile            # Docker configuration
├── nginx.conf            # Nginx configuration for Docker
├── package.json          # Dependencies and scripts
└── tsconfig.json         # TypeScript configuration
```

## Features

- **Conversational Search**: Users can search for products using natural language
- **Product Display**: Products are displayed in a responsive grid
- **Dark Mode**: Toggle between light and dark mode
- **Responsive Design**: Works on all screen sizes
- **Hover Details**: Additional product details shown on hover

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. Clone the repository
2. Install dependencies:

```bash
cd frontend
npm install
```

### Development

Run the development server:

```bash
npm run dev
```

The application will be available at http://localhost:5173.

### Building for Production

Build the application:

```bash
npm run build
```

### Docker

Build and run with Docker:

```bash
docker build -t ai-commerce-frontend .
docker run -p 80:80 ai-commerce-frontend
```

## Integration with Backend

The frontend is designed to work with the AI-Native Commerce Platform backend. The API integration layer in `src/api/` handles the communication with the backend.

## Environment Variables

- `VITE_API_BASE_URL`: The URL of the backend API (default: http://localhost:5000)
