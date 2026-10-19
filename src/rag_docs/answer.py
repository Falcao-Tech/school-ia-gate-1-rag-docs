from rag_docs.llm import Chat, Embedder
from rag_docs.models import Answer, Hit
from rag_docs.store import VectorStore

NOT_FOUND = "Não encontrei isso na documentação do time."


def build_messages(question: str, hits: list[Hit]) -> list[dict[str, str]]:
    """Monta as mensagens do chat no formato [{"role": ..., "content": ...}].

    Contrato (ver tests/test_answer.py):
    - A primeira mensagem é a instrução de sistema (role "system"): responder só com base nos
      trechos, citar a fonte entre colchetes (ex.: [projeto-x/README.md]) e dizer que não
      encontrou quando os trechos não respondem.
    - A última mensagem (role "user") traz cada trecho com a fonte entre colchetes, o texto do
      trecho e a pergunta.
    """
    # TODO: implemente.
    raise NotImplementedError("build_messages")


def cited_sources(text: str, hits: list[Hit]) -> list[str]:
    """Fontes citadas entre colchetes na resposta, na ordem em que aparecem e sem repetir.

    Só valem fontes que vieram da busca: citação inventada pelo modelo é descartada.
    """
    # TODO: implemente.
    raise NotImplementedError("cited_sources")


def answer_question(
    question: str,
    embedder: Embedder,
    store: VectorStore,
    chat: Chat,
    k: int = 4,
    min_score: float = 0.7,
) -> Answer:
    """Pergunta → embedding → busca → resposta citando as fontes.

    Contrato (ver tests/test_answer.py):
    - Busca os k trechos e descarta os com score abaixo de min_score.
    - Sem trecho sobrando: devolve Answer(text=NOT_FOUND) SEM chamar o modelo.
    - Com trechos: chama chat.complete(build_messages(...)) e devolve Answer com
      text = resposta, sources = cited_sources(...) e consulted = fontes dos trechos enviados
      (sem repetir, na ordem da busca).
    """
    # TODO: implemente.
    raise NotImplementedError("answer_question")
