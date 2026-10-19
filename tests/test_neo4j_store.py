"""Teste de integração do Neo4jStore. Rode com: docker compose up -d && uv run pytest -m integration"""

import os
from pathlib import Path

import pytest
from fakes import DIMENSIONS, HashEmbedder
from neo4j import GraphDatabase

from rag_docs.ingest import ingest_folder
from rag_docs.store import Neo4jStore

pytestmark = pytest.mark.integration
DOCS = Path(__file__).parent.parent / "docs" / "exemplo"


@pytest.fixture
def store():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    auth = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "noclaf-school"))
    with GraphDatabase.driver(uri, auth=auth) as driver:
        driver.execute_query("MATCH (n) WHERE n:Document OR n:Chunk DETACH DELETE n")
        driver.execute_query("DROP INDEX chunk_embedding IF EXISTS")
        store = Neo4jStore(driver, DIMENSIONS)
        store.setup()
        yield store


def test_busca_traz_o_trecho_mais_parecido_primeiro(store: Neo4jStore):
    embedder = HashEmbedder()
    ingest_folder(DOCS, embedder, store)

    [vector] = embedder.embed(["Por que escolhemos Postgres como banco?"])
    hits = store.search(vector, k=3)

    assert hits[0].chunk.source == "adr/0001-postgres.md"
    assert hits[0].score >= hits[-1].score
    assert len(hits) == 3


def test_reingestao_nao_duplica_trechos(store: Neo4jStore):
    embedder = HashEmbedder()
    first = ingest_folder(DOCS, embedder, store)
    ingest_folder(DOCS, embedder, store)

    records, _, _ = store.driver.execute_query("MATCH (c:Chunk) RETURN count(c) AS total")
    assert records[0]["total"] == sum(first.values())
