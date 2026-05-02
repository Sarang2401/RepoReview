import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

def get_embeddings():
    # all-MiniLM-L6-v2 is fast, lightweight, and excellent for code/text similarity
    # Runs locally — no API key or rate limits needed
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def create_vector_store(docs):
    persist_dir = "chroma_db"
    
    db = Chroma.from_documents(
        documents=docs,
        embedding=get_embeddings(),
        persist_directory=persist_dir
    )
    return db


def load_vector_store():
    return Chroma(
        persist_directory="chroma_db",
        embedding_function=get_embeddings()
    )