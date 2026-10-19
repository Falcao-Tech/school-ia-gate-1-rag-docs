from pathlib import Path

from rag_docs.chunker import chunk_document
from rag_docs.llm import Embedder
from rag_docs.loader import load_documents
from rag_docs.store import VectorStore

BATCH = 64


def ingest_folder(folder: str | Path, embedder: Embedder, store: VectorStore) -> dict[str, int]:
    """Lê a pasta, quebra em trechos, gera embeddings e grava. Devolve trechos por documento."""
    summary = {}
    for doc in load_documents(folder):
        chunks = chunk_document(doc)
        texts = [f"{c.heading}\n\n{c.text}" if c.heading else c.text for c in chunks]
        vectors = [v for i in range(0, len(texts), BATCH) for v in embedder.embed(texts[i:i + BATCH])]
        store.replace_source(doc.source, chunks, vectors)
        summary[doc.source] = len(chunks)
    return summary
