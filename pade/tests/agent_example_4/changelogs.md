# Changelog - agent_example_4

## Objetivo atual
- Demonstrar o protocolo FIPA Contract Net no PADE novo.
- Comparar propostas de dois participantes e selecionar a melhor resposta.

## Estado verificado no PADE novo
- O arquivo principal e `agent_example_4_updated.py`.
- A execucao recomendada e `pade start-runtime --port 24000 agent_example_4_updated.py`.
- O exemplo usa sessao compartilhada do runtime e AIDs completos no novo formato.
- O iniciador envia um `CFP`, recebe duas propostas, rejeita a oferta inferior, aceita a melhor e recebe o `INFORM` final.

## Ajustes consolidados
- O changelog antigo desta pasta estava incorreto e foi reescrito do zero.
- O exemplo atual esta alinhado ao fluxo integrado do runtime.
- O contrato foi validado com logs consistentes em `messages.csv` e `events.csv`.
- A selecao da melhor proposta ficou documentada como parte do comportamento esperado.

## Logs esperados
- `messages.csv`: `2 cfp`, `2 propose`, `1 reject-proposal`, `1 accept-proposal` e `1 inform`.
- `agents.csv`: sniffer, dois participantes e um iniciador.
- `events.csv`: criacao dos agentes, inicio do Contract Net, recepcao de propostas, selecao da melhor oferta e encerramento do protocolo.

## Observacao
- Este exemplo representa o primeiro fluxo completo de negociacao entre varios agentes ja totalmente coerente com a telemetria CSV do PADE novo.
