from pathlib import Path

from rag_docs.models import Document

EXTENSIONS = {".md", ".mdx", ".txt"}


def load_documents(folder: str | Path) -> list[Document]:
    """Lê todos os arquivos de texto da pasta (recursivo), ordenados pelo caminho."""
    root = Path(folder)
    if not root.is_dir():
        raise FileNotFoundError(f"Pasta não encontrada: {root}")
    documents = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in EXTENSIONS:
            text = path.read_text(encoding="utf-8").strip()
            if text:
                documents.append(Document(source=path.relative_to(root).as_posix(), text=text))
    return documents
