from rag_docs.models import Chunk, Document


def chunk_document(doc: Document, max_chars: int = 1200, overlap: int = 200) -> list[Chunk]:
    """Quebra um documento em trechos por seção, respeitando max_chars.

    Contrato (ver tests/test_chunker.py):
    - Cada cabeçalho markdown (#, ##, ...) abre uma seção; o texto antes do primeiro cabeçalho
      é uma seção com título "". Seções sem corpo não geram trecho.
    - Chunk.heading é o título da seção; Chunk.text é o corpo, sem o cabeçalho.
    - Seção maior que max_chars vira vários trechos de até max_chars, cortados em espaço
      (nunca no meio de uma palavra) e com cerca de `overlap` caracteres repetidos entre
      trechos vizinhos, para não perder contexto no corte.
    - Chunk.id é "<source>#<índice>", com índice sequencial no documento todo, a partir de 0.
    - overlap >= max_chars é ValueError.
    """
    # TODO: implemente. Dica: re.finditer com re.MULTILINE acha os cabeçalhos.
    raise NotImplementedError("chunk_document")
