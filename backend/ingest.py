import os
import shutil
from git import Repo
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def clone_repo(repo_url, path="data/repos"):
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    repo_path = os.path.join(path, repo_name)

    # Ensure the base directory exists
    os.makedirs(path, exist_ok=True)

    if os.path.exists(repo_path):
        # Remove existing repo to get a fresh clone
        try:
            import stat
            def remove_readonly(func, path, _):
                os.chmod(path, stat.S_IWRITE)
                func(path)
            shutil.rmtree(repo_path, onerror=remove_readonly)
        except Exception as e:
            print(f"Warning: could not remove old repo: {e}")

    Repo.clone_from(repo_url, repo_path)
    return repo_path


def load_files(repo_path):
    docs = []
    # Relevant file extensions for a typical repo explainer
    allowed_extensions = {".py", ".js", ".ts", ".md", ".java", ".go", ".c", ".cpp", ".html", ".css", ".json"}
    
    for root, _, files in os.walk(repo_path):
        if ".git" in root or "node_modules" in root or "venv" in root or "__pycache__" in root:
            continue
            
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in allowed_extensions:
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        if content.strip():
                            # Path relative to repo to display nicely
                            rel_path = os.path.relpath(full_path, repo_path)
                            docs.append(Document(page_content=content, metadata={"file": rel_path}))
                except Exception as e:
                    print(f"Error reading {full_path}: {e}")
                    
    # Split documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    
    split_docs = text_splitter.split_documents(docs)
    return split_docs