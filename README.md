# Gate 1 · RAG sobre a documentação do time

Desafio da **Fase 1 (Fundamentos de IA e LLMs)** da trilha de Engenharia de Software com IA
Aplicada do Noclaf School.

Você vai construir um RAG em Python que responde perguntas sobre a documentação do time
(READMEs, ADRs, wiki) e **cita de onde tirou a resposta**. A base que você indexar aqui volta
mais tarde como uma das fontes do copiloto do time.

## Critério de aprovação

- Responde *"Como rodo o projeto X?"* com base num README real do time
- Responde *"Por que escolhemos Y?"* citando o ADR de origem
- Você explica o fluxo (chunk → embedding → busca → resposta) sem slide

## Como começar

1. Clique em **Use this template** e crie o repositório na **sua conta pessoal**.
   - Vai indexar documentação interna? Crie como **privado** e dê acesso de leitura a quem
     revisa o gate. Documentação interna não vai para repositório público.
2. Clone e instale (precisa de [uv](https://docs.astral.sh/uv/) e Docker):

   ```bash
   uv sync
   cp .env.example .env      # escolha OpenRouter ou Ollama e preencha
   docker compose up -d      # sobe o Neo4j (painel em http://localhost:7474)
   ```

3. Rode os testes. **Eles começam vermelhos de propósito**: cada teste que falha é uma parte
   do desafio.

   ```bash
   uv run pytest                  # testes de unidade (sem Neo4j nem modelo)
   uv run pytest -m integration   # teste do Neo4j (precisa do docker compose up)
   ```

   O teste de integração **apaga** os nós `Document` e `Chunk` do Neo4j local para começar
   limpo. Reindexe depois de rodá-lo.

## O que você implementa

Tudo o que não está nesta lista já funciona: leitura dos arquivos, cliente do modelo, CLI,
gravação no Neo4j e os dublês de teste. Procure por `TODO` no código.

| Arquivo | O que fazer | Testes |
|---|---|---|
| `src/rag_docs/chunker.py` | `chunk_document`: quebrar o markdown em trechos por seção, com tamanho máximo e sobreposição | `tests/test_chunker.py` |
| `src/rag_docs/store.py` | `Neo4jStore.search`: busca vetorial no índice `chunk_embedding` | `tests/test_neo4j_store.py` |
| `src/rag_docs/answer.py` | `build_messages`, `cited_sources` e `answer_question`: montar o prompt, chamar o modelo e devolver só as fontes que vieram da busca | `tests/test_answer.py` |

Leia os testes antes de começar: eles são a especificação. Não altere os testes para passar;
se achar que um teste está errado, leve para a demo de sexta.

## Usando

```bash
uv run rag-docs ingest docs/                          # indexa a pasta
uv run rag-docs ask "Como rodo o projeto X?"          # pergunta
uv run rag-docs search "Por que escolhemos Postgres?" # mostra trechos e scores
```

A pasta `docs/exemplo/` tem um README e um ADR de mentira, só para você testar. Para o gate,
troque pelos documentos reais do time: copie READMEs e ADRs para `docs/` (ou aponte o `ingest`
para outra pasta) e rode o `ingest` de novo. Reindexar o mesmo arquivo substitui os trechos
antigos.

## Calibrando o MIN_SCORE

`MIN_SCORE` decide se um trecho é relevante o bastante para ir para o modelo. Abaixo dele, a
resposta é "Não encontrei isso na documentação do time" e o modelo nem é chamado.

O score do índice vetorial do Neo4j com cosseno é `(1 + cosseno) / 2`, então vai de 0 a 1 e
**um trecho sem relação nenhuma raramente fica abaixo de 0,5**. O ponto de corte certo depende
do modelo de embedding. Para achar o seu:

1. Rode `uv run rag-docs search` com 3 perguntas que a documentação responde e 3 que não
   responde (ex.: "Qual a receita de bolo de cenoura?").
2. Escolha um valor entre o maior score das irrelevantes e o menor das relevantes.

Como referência: com `nomic-embed-text`, perguntas relevantes ficaram acima de 0,83 e
irrelevantes abaixo de 0,82.

## Escolhendo o modelo

- **OpenRouter** (`openai/text-embedding-3-small` + `openai/gpt-4o-mini`): o caminho mais
  simples, cita as fontes direitinho.
- **Ollama local** (`nomic-embed-text` + `llama3.2`): grátis e nada sai da sua máquina. Modelos
  pequenos às vezes esquecem de citar a fonte; nesse caso a CLI mostra os trechos consultados.
  Para o gate a resposta precisa citar, então use um modelo que siga a instrução.

Trocar o modelo de embedding muda a dimensão dos vetores: ajuste `EMBEDDING_DIMENSIONS`, apague
o índice (`DROP INDEX chunk_embedding` no painel do Neo4j) e reindexe.

## Entrega

1. Testes verdes: `uv run pytest && uv run pytest -m integration`.
2. Documentação real do time indexada, respondendo às duas perguntas do critério com citação.
3. Envie o link do seu repositório na etapa **Gate 1** do Noclaf School (`/school` no NOS).
4. Na revisão, você explica o fluxo sem slide.
