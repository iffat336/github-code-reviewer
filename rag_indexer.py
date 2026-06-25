"""Repository indexing and semantic context retrieval."""

import os

import chromadb

from github_client import get_repository

COLLECTION_NAME = "codebase"
INDEX_PATH = "./codebase_index"
SUPPORTED_EXTENSIONS = {".py", ".js", ".ts", ".java", ".go", ".rb", ".php", ".cs"}


def get_collection(recreate: bool = False):
    """Open the ChromaDB collection lazily to avoid import-time side effects."""
    client = chromadb.PersistentClient(path=INDEX_PATH)
    if recreate:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
    return client.get_or_create_collection(COLLECTION_NAME)


def index_repository(recreate: bool = True) -> int:
    """Download and index supported source files from the configured repo."""
    repo = get_repository()
    collection = get_collection(recreate=recreate)

    print(f"Indexing repository: {repo.full_name}")
    contents = list(repo.get_contents(""))
    files_indexed = 0

    while contents:
        item = contents.pop(0)
        if item.type == "dir":
            contents.extend(repo.get_contents(item.path))
            continue

        if os.path.splitext(item.name)[1].lower() not in SUPPORTED_EXTENSIONS:
            continue

        try:
            code = item.decoded_content.decode("utf-8")
            collection.upsert(
                documents=[code[:2000]],
                ids=[item.path],
                metadatas=[{"path": item.path}],
            )
            files_indexed += 1
            print(f"  Indexed: {item.path}")
        except Exception as exc:
            print(f"  Skipped {item.path}: {exc}")

    print(f"\nDone! Indexed {files_indexed} files.")
    return files_indexed


def search_codebase(query: str, top_k: int = 3) -> str:
    """Search the indexed codebase and render the best matching snippets."""
    collection = get_collection()
    count = collection.count()
    if count == 0:
        return ""

    results = collection.query(query_texts=[query], n_results=min(top_k, count))
    documents = results.get("documents") or [[]]
    metadata = results.get("metadatas") or [[]]
    if not documents[0]:
        return ""

    sections = ["Relevant code from the codebase:"]
    for document, item_metadata in zip(documents[0], metadata[0]):
        sections.append(f"\n--- {item_metadata['path']} ---\n{document}")
    return "\n".join(sections)
