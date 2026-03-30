# Changelog - agent_example_3

## Objetivo atual
- Demonstrar o protocolo FIPA Request com um agente de relogio e um agente de tempo.
- Garantir que o inicio da conversa aconteca somente depois da propagacao da tabela do AMS.

## Estado verificado no PADE novo
- O arquivo principal e `agent_example_3_updated.py`.
- A execucao recomendada e `pade start-runtime --port 24000 agent_example_3_updated.py`.
- O exemplo usa sessao compartilhada do runtime.
- O `ClockAgent` espera a tabela do AMS por meio de um comportamento de monitoramento antes de iniciar os `REQUEST`.

## Ajustes consolidados
- As instrucoes antigas baseadas em AMS separado e inicializacao manual ficaram obsoletas.
- O fluxo atual usa o runtime integrado do PADE novo.
- A sincronizacao com a tabela do AMS foi tornada explicita para evitar o envio prematuro de mensagens.
- O comportamento final e ciclico: `REQUEST` do relogio e `INFORM` com horario retornado pelo agente de tempo.

## Logs esperados
- `agents.csv`: sniffer, `clock_agent` e `time_agent`.
- `messages.csv`: alternancia entre `request` e `inform`.
- `events.csv`: inicio do teste, agentes iniciados, `request_sent`, `request_received`, `response_sent` e `inform_received`.

## Observacao
- Este exemplo continua periodico por projeto. O objetivo aqui nao e uma conversa unica, mas sim a repeticao controlada do protocolo Request.
