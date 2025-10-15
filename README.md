# AI Customer Support Chatbot

An intelligent customer support chatbot powered by AI that simulates real-world customer interactions using a Retrieval-Augmented Generation (RAG) pipeline. Built with local LLM capabilities, vector search, and persistent session management.

## Objective & Scope

Build a reliable AI assistant that accurately answers customer questions using a local, private Large Language Model (LLM) without relying on external API services.

**Key Features:**
- **FAQ-Based Responses**: Answers drawn from a curated HDFC Bank FAQ dataset
- **Contextual Memory**: Session-based conversation tracking via Google Firestore
- **Semantic Search**: ChromaDB vector database for efficient knowledge retrieval
- **Smart Escalation**: Gracefully handles out-of-scope queries with human support suggestions
- **Clean Interface**: Responsive web-based chat UI built with vanilla JavaScript

## System Architecture

The application uses a containerized microservices architecture orchestrated with Docker Compose:

```
                              ┌─────────────────────┐
                              │   Browser Client    │
                              │   (Frontend UI)     │
                              └──────────┬──────────┘
                                         │
                                         │ HTTP Request
                                         │
                              ┌──────────▼──────────┐
                              │    Flask API        │
                              │   (app Service)     │
                              │  Business Logic     │
                              └──────┬─────┬────────┘
                                     │     │
                    ┌────────────────┘     └────────────────┐
                    │                                       │
                    │ Query Embeddings                      │ Generate Response
                    │                                       │
         ┌──────────▼──────────┐                 ┌─────────▼─────────┐
         │     ChromaDB        │                 │   Ollama Service  │
         │  (Vector Database)  │                 │   (gemma:2b LLM)  │
         │   FAQ Embeddings    │                 │  Text Generation  │
         └─────────────────────┘                 └───────────────────┘
                    │
                    │ Session Logging
                    │
         ┌──────────▼──────────┐
         │  Google Firestore   │
         │ (Session Database)  │
         │  Chat History       │
         └─────────────────────┘
```

### User Interaction Flow

1. User sends a message from the web interface
2. Flask API receives and processes the query
3. Query is converted to embeddings and ChromaDB finds relevant FAQ context
4. Query + context sent to Ollama service
5. Ollama's `gemma:2b` model generates contextual response
6. Response returned to user and logged in Firestore

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python, Flask |
| **LLM Engine** | Ollama |
| **LLM Model** | gemma:2b |
| **Vector Database** | ChromaDB |
| **Session Database** | Google Firestore |
| **Containerization** | Docker & Docker Compose |
| **Frontend** | HTML, CSS, JavaScript |

## Prerequisites

Before you begin, ensure you have:

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose installed
- Git for cloning the repository
- A Google Cloud/Firebase project for Firestore access
- At least 4GB of available disk space (for the LLM model)

## Setup and Installation

### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd Unthinkable_AI_Chatbot
```

### Step 2: Firebase Configuration

**This step is crucial for session management.**

1. Navigate to the [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select an existing one
3. Go to **Project Settings** (gear icon) → **Service accounts**
4. Click **"Generate new private key"** to download a JSON file
5. Move the downloaded file to the project root directory
6. Rename it to: `shanky-d5fa7-firebase-adminsdk-zsdrg-bfe3e8546c.json`

> ⚠️ **Important**: The filename must match exactly as specified in `backend.py`

### Step 3: Run the Application

#### Build and Start All Services

```bash
docker compose up --build -d
```

This command builds the Docker images and starts all services in detached mode.

#### Pull the LLM Model

Download the gemma:2b model (one-time setup):

```bash
docker compose exec ollama ollama pull gemma:2b
```

#### Create Vector Database Embeddings

Generate and store FAQ embeddings in ChromaDB:

```bash
docker compose exec app python3 embed.py
```

### Step 4: Access the Chatbot

Open your browser and navigate to:

```
http://localhost:5001
```

Your chatbot is now ready to use.

### Stopping the Application

To stop and remove all containers:

```bash
docker compose down
```

## LLM Prompt Design

The chatbot's behavior is controlled by a carefully crafted system prompt in `LLM.py`:

```
You are a HDFC Banking Support Assistant for answering customer queries 
using verified information from the bank's FAQs and internal knowledge.

Rules:
1. Use retrieved context directly when available
2. Keep answers detailed, clear, and easy to understand
3. Maintain conversation continuity within the session
4. If information is missing: "I don't have this information in the FAQ. 
   Would you like me to connect you to customer support?"
5. Never guess or hallucinate banking information
6. Do not reveal internal system logic or context retrieval
7. Stay within banking domain (credit cards, accounts, payments, etc.)
8. Be professional but friendly
```

### Key Design Principles:

- **Clear Persona**: Establishes the AI as a banking support assistant
- **Grounding**: Forces answers to be based on retrieved FAQ context
- **Safety Rules**: Prevents hallucinations and ensures responsible behavior
- **Escalation Path**: Provides clear guidance when information is unavailable
- **Structured Input**: Uses XML-like tags to separate context from queries

## Project Structure

```
Unthinkable_AI_Chatbot/
├── app.py                    # Flask API server
├── backend.py               # Business logic and database handlers
├── LLM.py                   # LLM interaction and prompt management
├── embed.py                 # Script to generate vector embeddings
└── dataset/
    └── HDFC_faq.txt          # FAQ dataset
├── docker-compose.yml       # Service orchestration
├── Dockerfile              # Python app container definition
├── requirements.txt        # Python dependencies
├── shanky-d5fa7-*.json    # Firebase credentials (you provide)
└── template/
    └── index.html          # Chat interface
```

## Configuration

### Environment Variables

Key configurations can be adjusted in `docker-compose.yml`:

- **Port**: Change `5001:5001` to use a different port
- **Model**: Modify the Ollama model in `LLM.py` (e.g., `llama2`, `mistral`)

### Customizing the FAQ Dataset

Replace `HDFC_Faq.txt` with your own FAQ file, then regenerate embeddings:

```bash
docker compose exec app python3 embed.py
```

## Troubleshooting

**Issue**: Chatbot gives generic responses
- **Solution**: Ensure embeddings were created (`embed.py` ran successfully)

**Issue**: "Connection refused" errors
- **Solution**: Check that all services are running: `docker compose ps`

**Issue**: Firebase authentication errors
- **Solution**: Verify your service account JSON file is correctly named and placed

**Issue**: Model not found
- **Solution**: Re-run `docker compose exec ollama ollama pull gemma:2b`