# Changelog - agent_example_1

## Objetivo atual
- Demonstrar uma comunicacao basica em anel entre tres agentes.
- Separar claramente o texto exibido no terminal do conteudo ACL enviado pela rede.

## Estado verificado no PADE novo
- O arquivo principal e `agent_example_1_updated.py`.
- A execucao recomendada e `pade start-runtime --port 24000 agent_example_1_updated.py`.
- O exemplo usa uma sessao compartilhada do runtime para manter `sessions.csv`, `agents.csv`, `messages.csv` e `events.csv` coerentes.
- O comportamento funcional atual e um anel de tres agentes que enviam `INFORM` em sequencia.

## Ajustes consolidados
- O fluxo antigo de inicializacao manual foi substituido pelo runtime integrado.
- O texto `Hello World! (Apenas Terminal)` permaneceu como saida local.
- As mensagens de rede passaram a usar um conteudo proprio, `Hello World Message! (Via Rede)`, com ontologia `hello_ontology`.
- Os logs agora registram o trafego real da aplicacao, sem depender de banco relacional.

## Logs esperados
- `agents.csv`: sniffer mais tres agentes do exemplo.
- `messages.csv`: tres mensagens `inform`.
- `events.csv`: abertura do teste, inicializacao dos agentes e o ciclo `message_sent -> message_received -> message_stored`.

## Observacao
- O `content` gravado em `messages.csv` representa a mensagem ACL enviada na rede, nao a frase impressa apenas no terminal.
