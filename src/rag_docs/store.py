from typing import Protocol

from neo4j import Driver

from rag_docs.models import Chunk, Hit

INDEX_NAME = "chunk_embedding"


class VectorStore(Protocol):
    def replace_source(self, source: str, chunks: list[Chunk], vectors: list[list[float]]) -> None: ...
    def search(self, vector: list[float], k: int) -> list[Hit]: ...


class Neo4jStore:
    """Guarda (:Document)-[:HAS_CHUNK]->(:Chunk) com um índice vetorial nos trechos."""

    def __init__(self, driver: Driver, dimensions: int):
        self.driver, self.dimensions = driver, dimensions

    def setup(self) -> None:
        with self.driver.session() as session:
            session.run(
                f"""
                CREATE VECTOR INDEX {INDEX_NAME} IF NOT EXISTS
                FOR (c:Chunk) ON c.embedding
                OPTIONS {{indexConfig: {{
                  `vector.dimensions`: {int(self.dimensions)},
                  `vector.similarity_function`: 'cosine'
                }}}}
                """
            ).consume()
            session.run("CALL db.awaitIndexes(300)").consume()

    def replace_source(self, source: str, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        """Apaga os trechos antigos do documento e grava os novos (reingestão idempotente)."""
        rows = [
            {"id": c.id, "heading": c.heading, "text": c.text, "embedding": v}
            for c, v in zip(chunks, vectors, strict=True)
        ]
        with self.driver.session() as session:
            session.execute_write(lambda tx: tx.run(
                """
                MERGE (d:Document {source: $source})
                WITH d
                OPTIONAL MATCH (d)-[:HAS_CHUNK]->(old:Chunk)
                DETACH DELETE old
                WITH DISTINCT d
                UNWIND $rows AS row
                CREATE (c:Chunk {id: row.id, source: $source, heading: row.heading, text: row.text})
                WITH d, c, row
                CALL db.create.setNodeVectorProperty(c, 'embedding', row.embedding)
                MERGE (d)-[:HAS_CHUNK]->(c)
                """,
                source=source,
                rows=rows,
            ).consume())

    def search(self, vector: list[float], k: int) -> list[Hit]:
        """Os k trechos mais parecidos com o vetor, do mais para o menos parecido.

        Use o procedimento db.index.vector.queryNodes sobre o índice INDEX_NAME e monte um Hit
        (Chunk + score) por resultado. O nó :Chunk tem as propriedades id, source, heading e text.
        """
        # TODO: implemente.
        raise NotImplementedError("Neo4jStore.search")
