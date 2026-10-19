from typing import Protocol

from openai import OpenAI


class Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


class Chat(Protocol):
    def complete(self, messages: list[dict[str, str]]) -> str: ...


class OpenAICompatibleEmbedder:
    """Embeddings por qualquer API compatível com OpenAI (OpenRouter, Ollama, OpenAI)."""

    def __init__(self, client: OpenAI, model: str):
        self.client, self.model = client, model

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in sorted(response.data, key=lambda item: item.index)]


class OpenAICompatibleChat:
    def __init__(self, client: OpenAI, model: str, temperature: float = 0.0):
        self.client, self.model, self.temperature = client, model, temperature

    def complete(self, messages: list[dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            model=self.model, messages=messages, temperature=self.temperature
        )
        return response.choices[0].message.content or ""
