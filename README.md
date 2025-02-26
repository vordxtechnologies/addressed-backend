***# Addressed FastAPI Backend

## Overview
The **Addressed FastAPI Backend** is a high-performance API framework built with **FastAPI**, designed to handle authentication, AI processing, and data integration. It leverages **Firestore, ChromaDB, Redis, Celery, and external APIs** to ensure scalability, efficiency, and extensibility.

## Core Tech Stack
- **FastAPI**: ASGI-based web framework for building APIs.
- **Firestore**: NoSQL document-based storage.
- **Firebase Authentication**: OAuth and JWT authentication.
- **Redis**: Caching Firestore queries to enhance performance.
- **Celery**: Asynchronous task queue for background processing.
- **ChromaDB**: Vector database for AI-powered search and embeddings.
- **LangChain**: AI-driven workflows and integrations.
- **Hugging Face Inference API**: AI model inference.
- **Deepseeck R1 & Janus Pro**: Backend AI inference models.
- **Ticketmaster API**: Retrieves concert event data.
- **Amazon API**: Fetches product data for AI recommendations.
- **Midjourney API**: AI-powered image generation.

---

## Project Structure
```
addressed-fastapi/
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── ai.py
│   │   ├── data.py
│   │   └── scrape.py
│   ├── core/
│   │   ├── security.py
│   │   └── config.py
│   ├── db/
│   │   ├── firestore.py
│   │   ├── redis.py
│   │   └── chromadb.py
│   ├── models/
│   │   └── user.py
│   ├── services/
│   │   ├── user_service.py
│   │   └── ai_service.py
│   ├── workers/
│   │   └── celery.py
│   └── main.py
├── .env
├── requirements.txt
└── README.md
```

---

## API Endpoints & Data Flow

### Authentication & User Management
- **POST** `/auth/signup` - Register new users (via Firebase Auth).
- **POST** `/auth/login` - Authenticate users and generate JWT tokens.
- **GET** `/user/profile` - Retrieve user profile from Firestore.
- **PUT** `/user/profile` - Update user details.
- **DELETE** `/user/account` - Delete user account.

### AI Processing & Inference
- **POST** `/ai/chroma-query` - Query ChromaDB for vector search.
- **POST** `/ai/huggingface-infer` - Run inference using Hugging Face models.
- **POST** `/ai/deepseeck-r1` - Process data with Deepseeck R1.
- **POST** `/ai/deepseeck-janus` - Run inference with Janus Pro.
- **POST** `/ai/langchain` - Query AI models via LangChain.
- **GET** `/ai/midjourney-generate` - Retrieve AI-generated images.

### Data Processing & API Integration
- **GET** `/data/concerts` - Fetch concert events from Ticketmaster API.
- **GET** `/data/products` - Fetch product data from Amazon API.
- **POST** `/data/process` - Execute data processing via Celery.

### Web Scraping & Caching
- **GET** `/scrape` - Initiate web scraping using Scrapy + Playwright.
- **GET** `/cache/status` - Monitor Redis cache status.

---

## Setup Instructions

### Prerequisites
- Python **3.8+**
- Firebase Account (for authentication)
- Firestore Database
- Redis Server
- ChromaDB Account

### Installation
1. Clone the repository:
   ```bash
   git clone  https://github.com/tlow001/addressed_backend.git
   cd addressed_backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables in `.env`:
   ```ini
   FIREBASE_API_KEY=your_firebase_api_key
   FIREBASE_AUTH_DOMAIN=your_firebase_auth_domain
   FIREBASE_PROJECT_ID=your_firebase_project_id
   FIREBASE_STORAGE_BUCKET=your_firebase_storage_bucket
   FIREBASE_MESSAGING_SENDER_ID=your_firebase_messaging_sender_id
   FIREBASE_APP_ID=your_firebase_app_id
   FIREBASE_MEASUREMENT_ID=your_firebase_measurement_id
   JWT_SECRET_KEY=your_jwt_secret_key
   REDIS_URL=redis://localhost:6379/0
   CHROMADB_API_KEY=your_chromadb_api_key
   GOOGLE_APPLICATION_CREDENTIALS=addressed-firebase-adminsdk.json
   ```

5. Run the FastAPI application:
   ```bash
   uvicorn app.main:app --reload
   ```



---

## Scalability & Performance Considerations
- **ASGI Server (Uvicorn + Gunicorn)**: Supports high-concurrency requests.
- **Firestore Optimized Reads**: Cached with Redis to minimize direct queries.
- **Celery for Background Processing**: Efficient handling of AI inference and long-running tasks.
- **ChromaDB for Vector Search**: AI-powered recommendations.
- **Microservices Architecture**: Allows seamless service extension.
- **Containerized Deployment (Docker + Kubernetes)**: Ensures scalability.
- **CI/CD (GitHub Actions + Terraform)**: Automates deployments.
- **Monitoring (Prometheus + Grafana)**: Tracks performance metrics.

---

## Development Roadmap
1. **Enhance Redis Caching**: Improve Firestore query caching.
2. **Expand AI Endpoints**: Add more Hugging Face, Deepseeck, and LangChain endpoints.
3. **Extend External API Integrations**: More data sources from Ticketmaster, Amazon, etc.
4. **Optimize Celery Task Queues**: Streamline background processing.
5. **Improve Documentation**: Continuously update `README.md`.

---

