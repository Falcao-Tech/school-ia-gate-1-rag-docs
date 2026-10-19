from pathlib import Path

import pytest

from rag_docs.loader import load_documents


def test_le_markdown_recursivo_com_caminho_relativo(tmp_path: Path):
    (tmp_path / "projeto").mkdir()
    (tmp_path / "projeto" / "README.md").write_text("# Projeto\n\nConteúdo", encoding="utf-8")
    (tmp_path / "imagem.png").write_bytes(b"\x89PNG")
    (tmp_path / "vazio.md").write_text("   ", encoding="utf-8")

    docs = load_documents(tmp_path)

    assert [d.source for d in docs] == ["projeto/README.md"]
    assert docs[0].text.startswith("# Projeto")


def test_pasta_inexistente_da_erro_claro(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_documents(tmp_path / "nao-existe")
