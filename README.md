# Repo Explainer Agent (MLOps Edition) 🚀

An advanced, production-ready AI Agent that clones, chunks, embeds, and explains GitHub repositories using Retrieval-Augmented Generation (RAG). Built with **LangChain**, **FastAPI**, **Streamlit**, and powered by **Groq (Llama-3)** and **HuggingFace (Sentence-Transformers)**.

This repository is structured as a full **MLOps project**, featuring robust dependency management, automated CI/CD pipelines, containerization with Docker, and persistent local vector storage.

---

## 🏗️ Architecture

- **Frontend:** Streamlit (Chat UI, Session State Management)
- **Backend API:** FastAPI (REST endpoints for ingestion and querying)
- **Agent Orchestration:** LangChain v0.3 Core (LCEL pure runnables)
- **LLM Engine:** Groq API (`llama-3.3-70b-versatile`) for ultra-fast, high-quality reasoning.
- **Embeddings:** HuggingFace `all-MiniLM-L6-v2` (runs entirely locally, free, no rate limits).
- **Vector Database:** ChromaDB (persistent local storage on disk).
- **Infrastructure:** Docker, Docker Compose, GitHub Actions.

---

## 🛠️ Tech Stack & MLOps Features

- **Containerization:** Separate multi-stage Dockerfiles for frontend and backend to ensure isolated, reproducible environments.
- **CI/CD Pipeline:** GitHub Actions workflow (`.github/workflows/ci.yml`) automatically lints code and verifies Docker image builds on every push/PR.
- **Local Persistence:** Uses Docker Volumes to map `data/repos` and `chroma_db` out of the container so data survives restarts.
- **Pre-baked Models:** The backend Dockerfile pre-downloads the HuggingFace sentence transformer weights *at build time* rather than runtime, ensuring the container spins up instantly in production.
- **Security:** Strict `.gitignore` prevents leaking `.env`, DB stores, cloned code, or virtual environments.

---

## 🚀 Local Development Setup (Without Docker)

### 1. Prerequisites
- Python 3.11+
- Git installed on your system

### 2. Install Dependencies
```bash
# Create a virtual environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\Activate.ps1
# Activate it (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env` and fill in your keys:
```bash
cp .env.example .env
```
Add your Groq API key:
```env
GROQ_API_KEY="gsk_your_key_here"
```

### 4. Run the Application
You need two terminals.

**Terminal 1 (Backend):**
```bash
uvicorn backend.main:app --port 8000 --reload --reload-dir backend --reload-dir frontend
```

**Terminal 2 (Frontend):**
```bash
streamlit run frontend/app.py
```

---

## 🐳 Docker Deployment (Production / MLOps)

Deploying the application via Docker ensures it runs exactly the same on your local machine, a cloud VM (like AWS EC2 or DigitalOcean), or a Kubernetes cluster.

### 1. Prerequisites
- [Docker](https://docs.docker.com/get-docker/) installed and running.
- [Docker Compose](https://docs.docker.com/compose/install/) installed.
- Ensure your `.env` file is fully populated in the project root.

### 2. Build and Spin Up the Containers
From the root of the repository, run:
```bash
docker-compose up --build -d
```
*Note: The first build will take a few minutes as it downloads the base Python images and the HuggingFace embedding weights.*

### 3. Access the Application
- **Frontend UI:** `http://localhost:8501`
- **Backend API Docs:** `http://localhost:8000/docs`

### 4. Stopping the Application
```bash
docker-compose down
```
*(Your cloned repos and ChromaDB embeddings will remain safe in your local `data/` and `chroma_db/` folders thanks to Docker volumes!)*

---

## 🧠 How it Works (The RAG Pipeline)

1. **Ingest (`/ingest`):** 
   - Git clones the target repository.
   - `langchain-text-splitters` recursively splits code/markdown files into chunk sizes of 1000 characters.
   - `sentence-transformers` creates dense vector embeddings for each chunk.
   - Chunks and embeddings are stored persistently in ChromaDB.
2. **Query (`/query`):**
   - The user's question is embedded and a similarity search retrieves the top 5 most relevant code chunks.
   - A LangChain message array passes the system prompt, context chunks, and user query to the Groq Llama 3 model.
   - The LLM streams back a highly contextual, accurate answer referencing the specific source files used.

---

## 🔒 Security Notes
- Never commit your `.env` file.
- The `chroma_db/` folder is ignored in Git to prevent huge commit sizes and data leaks.
- The `data/repos/` folder is ignored to prevent pushing third-party code into your repository.
