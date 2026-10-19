import argparse

from neo4j import GraphDatabase
from openai import OpenAI

from rag_docs.answer import answer_question
from rag_docs.config import load_settings
from rag_docs.ingest import ingest_folder
from rag_docs.llm import OpenAICompatibleChat, OpenAICompatibleEmbedder
from rag_docs.store import Neo4jStore


def main() -> None:
    parser = argparse.ArgumentParser(prog="rag-docs", description="RAG sobre a documentação do time")
    commands = parser.add_subparsers(dest="command", required=True)
    ingest = commands.add_parser("ingest", help="indexa uma pasta de documentação")
    ingest.add_argument("folder")
    ask = commands.add_parser("ask", help="faz uma pergunta à documentação")
    ask.add_argument("question")
    ask.add_argument("-k", type=int, default=4, help="quantos trechos buscar")
    search = commands.add_parser("search", help="mostra os trechos e scores da busca (para calibrar MIN_SCORE)")
    search.add_argument("question")
    search.add_argument("-k", type=int, default=5)
    args = parser.parse_args()

    settings = load_settings()
    client = OpenAI(base_url=settings.llm_base_url, api_key=settings.llm_api_key)
    embedder = OpenAICompatibleEmbedder(client, settings.embedding_model)
    with GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)) as driver:
        store = Neo4jStore(driver, settings.embedding_dimensions)
        store.setup()
        if args.command == "ingest":
            summary = ingest_folder(args.folder, embedder, store)
            for source, count in summary.items():
                print(f"{count:>4} trechos  {source}")
            print(f"{len(summary)} documentos indexados.")
            return
        if args.command == "search":
            [vector] = embedder.embed([args.question])
            for hit in store.search(vector, args.k):
                preview = hit.chunk.text.replace("\n", " ")[:80]
                print(f"{hit.score:.3f}  {hit.chunk.id}  [{hit.chunk.heading}]  {preview}")
            return
        answer = answer_question(
            args.question, embedder, store, OpenAICompatibleChat(client, settings.chat_model),
            k=args.k, min_score=settings.min_score,
        )
        print(answer.text)
        if answer.sources:
            print("\nFontes citadas:")
            for source in answer.sources:
                print(f"- {source}")
        elif answer.consulted:
            print("\nO modelo não citou fonte. Trechos consultados:")
            for source in answer.consulted:
                print(f"- {source}")


if __name__ == "__main__":
    main()
