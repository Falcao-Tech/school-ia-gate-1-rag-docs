from pathlib import Path

from fakes import FakeChat, HashEmbedder, InMemoryStore

from rag_docs.answer import NOT_FOUND, answer_question, build_messages
from rag_docs.ingest import ingest_folder
from rag_docs.models import Chunk, Hit

DOCS = Path(__file__).parent.parent / "docs" / "exemplo"
# O HashEmbedder é bem mais "burro" que um modelo de embedding de verdade, então os scores
# dele são baixos. Nos testes o corte é explícito; no uso real ele vem de MIN_SCORE no .env.
MIN_SCORE = 0.15


def indexed_store() -> InMemoryStore:
    store = InMemoryStore()
    ingest_folder(DOCS, HashEmbedder(), store)
    return store


def test_mensagens_trazem_fonte_trecho_e_pergunta():
    hit = Hit(Chunk(id="a.md#0", source="a.md", heading="Como rodar", text="Rode make dev."), 0.9)

    messages = build_messages("Como rodo?", [hit])

    assert messages[0]["role"] == "system"
    assert "[a.md]" in messages[-1]["content"]
    assert "Rode make dev." in messages[-1]["content"]
    assert "Como rodo?" in messages[-1]["content"]


def test_responde_citando_a_fonte_encontrada():
    chat = FakeChat("Suba o banco com docker compose [projeto-x/README.md].")

    answer = answer_question("Como rodar o projeto X localmente?", HashEmbedder(), indexed_store(), chat, min_score=MIN_SCORE)

    assert answer.sources == ["projeto-x/README.md"]
    assert "projeto-x/README.md" in answer.consulted
    assert "projeto-x/README.md" in chat.calls[0][-1]["content"]


def test_pergunta_de_decisao_busca_o_adr():
    chat = FakeChat("Por causa do suporte a JSONB [adr/0001-postgres.md].")

    answer = answer_question("Por que escolhemos Postgres como banco?", HashEmbedder(), indexed_store(), chat, min_score=MIN_SCORE)

    assert answer.sources == ["adr/0001-postgres.md"]


def test_descarta_fonte_inventada_pelo_modelo():
    chat = FakeChat("Veja [projeto-x/README.md] e [manual-que-nao-existe.md].")

    answer = answer_question("Como rodar o projeto X localmente?", HashEmbedder(), indexed_store(), chat, min_score=MIN_SCORE)

    assert answer.sources == ["projeto-x/README.md"]


class StaticStore:
    def __init__(self, hits: list[Hit]):
        self.hits = hits

    def search(self, vector: list[float], k: int) -> list[Hit]:
        return self.hits[:k]


def test_sem_trecho_relevante_nao_chama_o_modelo():
    weak = Hit(Chunk(id="a.md#0", source="a.md", heading="", text="Outro assunto."), 0.12)
    chat = FakeChat("não deveria ser chamado")

    answer = answer_question("Qual a receita de bolo de cenoura?", HashEmbedder(), StaticStore([weak]), chat, min_score=0.3)

    assert answer.text == NOT_FOUND
    assert answer.sources == []
    assert chat.calls == []


def test_so_os_trechos_acima_do_corte_vao_para_o_modelo():
    strong = Hit(Chunk(id="a.md#0", source="a.md", heading="", text="Trecho relevante."), 0.8)
    weak = Hit(Chunk(id="b.md#0", source="b.md", heading="", text="Trecho fraco."), 0.1)
    chat = FakeChat("Resposta [a.md].")

    answer_question("Pergunta?", HashEmbedder(), StaticStore([strong, weak]), chat, min_score=0.3)

    prompt = chat.calls[0][-1]["content"]
    assert "Trecho relevante." in prompt
    assert "Trecho fraco." not in prompt
