import os
import traceback
import asyncio
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Explicitly point to the .env in the project root
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

from backend.ingest import clone_repo, load_files
from backend.retriever import create_vector_store, load_vector_store
from backend.agent import answer_query

# Global DB instance
db = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the vector store at startup without blocking the event loop."""
    global db
    if os.path.exists("chroma_db"):
        try:
            loop = asyncio.get_event_loop()
            # Run the blocking HuggingFace model load in a thread pool
            with ThreadPoolExecutor() as pool:
                db = await loop.run_in_executor(pool, load_vector_store)
            print("Loaded existing vector store.")
        except Exception as e:
            print(f"Could not load existing vector store: {e}")
    yield  # server is running
    # Cleanup on shutdown (if needed)

app = FastAPI(title="Repo Explainer API", lifespan=lifespan)

# Setup CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ingest")
def ingest_repo(repo_url: str):
    global db
    try:
        if not repo_url.startswith("http"):
            raise ValueError("Invalid URL format")
        
        print(f"[INGEST] Cloning: {repo_url}")
        repo_path = clone_repo(repo_url)
        print(f"[INGEST] Cloned to: {repo_path}")

        docs = load_files(repo_path)
        print(f"[INGEST] Loaded {len(docs)} document chunks")

        if not docs:
            raise ValueError("No supported files found in the repository.")

        print("[INGEST] Creating vector store...")
        db = create_vector_store(docs)
        print("[INGEST] Done!")
        return {"status": "Repo ingested successfully", "documents_processed": len(docs)}
    except Exception as e:
        traceback.print_exc()  # full traceback in terminal
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
def query_repo(query: str, level: str = "beginner"):
    global db
    if db is None:
        raise HTTPException(status_code=400, detail="No repository ingested yet. Please ingest a repository first.")
        
    try:
        response, sources = answer_query(db, query, level)
        return {"answer": response, "sources": sources}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))