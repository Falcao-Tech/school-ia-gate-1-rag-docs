# Projeto X

API de pedidos usada pelo app e pelo painel administrativo.

## Como rodar localmente

1. Suba o banco e a fila: `docker compose up -d`
2. Instale as dependências: `uv sync`
3. Rode as migrations: `uv run alembic upgrade head`
4. Suba a API: `uv run fastapi dev app/main.py`

A API fica em `http://localhost:8000` e a documentação em `/docs`.

## Variáveis de ambiente

Copie `.env.example` para `.env`. As obrigatórias são `DATABASE_URL` e `QUEUE_URL`.

## Deploy

Merge na `main` publica em produção pelo GitHub Actions. Não existe deploy manual.
