# Changelog - agent_example_2

## Objetivo atual
- Demonstrar o uso de comportamento temporal no PADE novo.
- Manter um exemplo principal simples e uma variante opcional que gere trafego ACL para estudo de logs.

## Estado verificado no PADE novo
- O exemplo principal e `agent_example_2_updated.py`.
- A variante didatica e `agent_example_2_with_messages.py`.
- A execucao recomendada continua sendo `pade start-runtime --port 24000 <arquivo>.py`.
- O exemplo principal imprime a atividade temporal periodica, mas nao precisa gerar mensagens ACL de aplicacao.

## Ajustes consolidados
- O exemplo principal foi mantido fiel ao objetivo original: temporizacao e exibicao em terminal.
- A variante com mensagens foi criada para mostrar `messages.csv` e `events.csv` de forma mais rica.
- Os logs atuais da pasta correspondem a essa variante com mensagens, nao ao exemplo principal puro.
- A variante envia `INFORM` periodico a cada terceiro disparo do temporizador.

## Logs esperados
- `agent_example_2_updated.py`: `messages.csv` pode permanecer vazio ou conter apenas rastros de infraestrutura fora da conversa de aplicacao.
- `agent_example_2_with_messages.py`: `messages.csv` registra `inform` com conteudo do tipo `Timed hello #<n>`.
- `events.csv`: em ambos os casos, deve registrar o inicio do teste e a atividade dos agentes temporais.

## Observacao
- Esta pasta contem dois objetivos complementares: um exemplo fiel ao legado e uma variante focada em telemetria ACL.
