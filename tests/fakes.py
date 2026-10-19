"""Dublês de teste: embeddings e chat determinísticos, sem chamar modelo nenhum."""

import hashlib
import math
import re
import unicodedata

from rag_docs.models import Chunk, Hit

DIMENSIONS = 2048
WORD = re.compile(r"\w+")
STOPWORDS = {"a", "o", "e", "de", "do", "da", "em", "um", "uma", "que", "para", "por", "com", "os", "as", "no", "na"}


def normalize(word: str) -> str:
    return unicodedata.normalize("NFKD", word.lower()).encode("ascii", "ignore").decode()


class HashEmbedder:
    """Saco de palavras com hash: textos com palavras em comum ficam parecidos."""

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._one(text) for text in texts]

    def _one(self, text: str) -> list[float]:
        vector = [0.0] * DIMENSIONS
        for word in WORD.findall(text):
            word = normalize(word)
            if word in STOPWORDS or len(word) < 3:
                continue
            bucket = int(hashlib.md5(word.encode()).hexdigest(), 16) % DIMENSIONS
            vector[bucket] += 1.0
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]


class InMemoryStore:
    """Store vetorial em memória (similaridade de cosseno), para testar sem Neo4j."""

    def __init__(self):
        self.rows: dict[str, tuple[Chunk, list[float]]] = {}

    def replace_source(self, source: str, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        self.rows = {k: v for k, v in self.rows.items() if v[0].source != source}
        for chunk, vector in zip(chunks, vectors, strict=True):
            self.rows[chunk.id] = (chunk, vector)

    def search(self, vector: list[float], k: int) -> list[Hit]:
        scored = [Hit(chunk, sum(a * b for a, b in zip(vector, v))) for chunk, v in self.rows.values()]
        return sorted(scored, key=lambda hit: hit.score, reverse=True)[:k]


class FakeChat:
    """Devolve uma resposta fixa e guarda as mensagens recebidas."""

    def __init__(self, reply: str):
        self.reply, self.calls = reply, []

    def complete(self, messages: list[dict[str, str]]) -> str:
        self.calls.append(messages)
        return self.reply
