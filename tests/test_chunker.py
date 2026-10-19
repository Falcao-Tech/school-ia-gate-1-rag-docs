from itertools import pairwise

import pytest

from rag_docs.chunker import chunk_document
from rag_docs.models import Document

DOC = Document(
    source="projeto-x/README.md",
    text="""Introdução sem título.

# Projeto X

Serviço de pedidos.

## Como rodar

Rode `docker compose up -d` e depois `uv run api`.

## Seção vazia

## Deploy

Merge na main publica sozinho.
""",
)


def test_um_trecho_por_secao_com_o_titulo():
    chunks = chunk_document(DOC)

    assert [(c.heading, c.text) for c in chunks] == [
        ("", "Introdução sem título."),
        ("Projeto X", "Serviço de pedidos."),
        ("Como rodar", "Rode `docker compose up -d` e depois `uv run api`."),
        ("Deploy", "Merge na main publica sozinho."),
    ]


def test_ids_sequenciais_com_a_fonte():
    chunks = chunk_document(DOC)

    assert [c.id for c in chunks] == [f"projeto-x/README.md#{i}" for i in range(4)]
    assert {c.source for c in chunks} == {"projeto-x/README.md"}


def test_secao_longa_vira_varios_trechos_sem_perder_palavra():
    words = [f"palavra{i}" for i in range(400)]
    doc = Document(source="longo.md", text="# Longo\n\n" + " ".join(words))

    chunks = chunk_document(doc, max_chars=300, overlap=60)

    assert len(chunks) > 1
    assert all(len(c.text) <= 300 for c in chunks)
    assert all(c.heading == "Longo" for c in chunks)
    joined = " ".join(c.text for c in chunks).split()
    assert set(words) <= set(joined)


def test_trechos_vizinhos_se_sobrepoem():
    doc = Document(source="longo.md", text=" ".join(f"w{i}" for i in range(300)))

    chunks = chunk_document(doc, max_chars=200, overlap=50)

    for current, following in pairwise(chunks):
        assert current.text.split()[-1] in following.text.split()


def test_corte_nao_parte_palavra_ao_meio():
    doc = Document(source="longo.md", text=" ".join(f"palavra{i}" for i in range(200)))

    for chunk in chunk_document(doc, max_chars=150, overlap=30):
        assert all(word.startswith("palavra") for word in chunk.text.split())


def test_overlap_maior_que_o_trecho_e_erro():
    with pytest.raises(ValueError):
        chunk_document(DOC, max_chars=100, overlap=100)
