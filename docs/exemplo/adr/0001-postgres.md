# ADR 0001: Postgres como banco principal

- **Status:** aceito
- **Data:** 2026-03-10

## Contexto

O Projeto X precisa guardar pedidos com itens de formato variável (cada cliente manda campos
diferentes) e ainda fazer relatórios com join entre pedidos, clientes e pagamentos.

## Decisão

Escolhemos o Postgres como banco principal, guardando os campos variáveis em colunas JSONB.

## Por que não MongoDB

Os relatórios dependem de join e de transação entre pedido e pagamento. No Postgres isso é
nativo; no MongoDB teríamos que montar na aplicação.

## Consequências

- Campos variáveis ficam em JSONB, com índice GIN quando forem filtrados.
- O time já opera Postgres nos outros projetos, então não há banco novo para manter.
