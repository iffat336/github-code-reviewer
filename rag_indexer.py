import os
import chromadb
from github import Github
from dotenv import load_dotenv

load_dotenv()

# ChromaDB stores your codebase as searchable vectors
chroma_client = chromadb.PersistentClient(path="./codebase_index")
collection = chroma_client.get_or_create_collection("codebase")

SUPPORTED_EXTENSIONS = [".py", ".js", ".ts", ".java", ".go", ".rb", ".php", ".cs"]

def index_repository():
    """Download and index all code files from the GitHub repo."""
    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPO")

    client = Github(token)
    repo = client.get_repo(repo_name)

    print(f"Indexing repository: {repo_name}")
    contents = repo.get_contents("")
    files_indexed = 0

    while contents:
        file = contents.pop(0)
        if file.type == "dir":
            contents.extend(repo.get_contents(file.path))
        else:
            ext = os.path.splitext(file.name)[1]
            if ext in SUPPORTED_EXTENSIONS:
                try:
                    code = file.decoded_content.decode("utf-8")
                    # Store in ChromaDB
                    collection.upsert(
                        documents=[code[:2000]],  # limit size per file
                        ids=[file.path],
                        metadatas=[{"path": file.path}]
                    )
                    files_indexed += 1
                    print(f"  Indexed: {file.path}")
                except Exception as e:
                    print(f"  Skipped {file.path}: {e}")

    print(f"\nDone! Indexed {files_indexed} files.")

def search_codebase(query: str, top_k: int = 3) -> str:
    """Search the indexed codebase for relevant code snippets."""
    results = collection.query(query_texts=[query], n_results=top_k)

    if not results["documents"][0]:
        return ""

    context = "Relevant code from the codebase:\n"
    for i, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
        context += f"\n--- {meta['path']} ---\n{doc}\n"

    return context
