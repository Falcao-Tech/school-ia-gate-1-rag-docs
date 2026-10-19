import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    llm_base_url: str
    llm_api_key: str
    embedding_model: str
    embedding_dimensions: int
    chat_model: str
    min_score: float
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str


def load_settings() -> Settings:
    load_dotenv()

    def required(name: str) -> str:
        value = os.getenv(name, "").strip()
        if not value:
            raise SystemExit(f"Variável {name} não configurada. Copie .env.example para .env e preencha.")
        return value

    return Settings(
        llm_base_url=required("LLM_BASE_URL"),
        llm_api_key=os.getenv("LLM_API_KEY", "ollama"),
        embedding_model=required("EMBEDDING_MODEL"),
        embedding_dimensions=int(required("EMBEDDING_DIMENSIONS")),
        chat_model=required("CHAT_MODEL"),
        min_score=float(os.getenv("MIN_SCORE", "0.7")),
        neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
        neo4j_password=os.getenv("NEO4J_PASSWORD", "noclaf-school"),
    )
