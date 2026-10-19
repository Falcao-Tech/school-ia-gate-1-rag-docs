from dataclasses import dataclass, field


@dataclass(frozen=True)
class Document:
    """Um arquivo de documentação lido do disco."""

    source: str  # caminho relativo à pasta ingerida, ex.: "projeto-x/README.md"
    text: str


@dataclass(frozen=True)
class Chunk:
    """Um trecho de um documento, pequeno o bastante para virar um embedding."""

    id: str  # "<source>#<índice>", ex.: "projeto-x/README.md#0"
    source: str
    heading: str  # título da seção de onde o trecho saiu ("" se não houver)
    text: str


@dataclass(frozen=True)
class Hit:
    """Um trecho devolvido pela busca, com a similaridade (0 a 1)."""

    chunk: Chunk
    score: float


@dataclass(frozen=True)
class Answer:
    text: str
    sources: list[str] = field(default_factory=list)  # fontes citadas na resposta
    consulted: list[str] = field(default_factory=list)  # fontes dos trechos enviados ao modelo
