# Changelog - mosaik_example

## Objetivo atual
- Integrar um agente PADE ao Mosaik e registrar os dados de co-simulacao como mensagens FIPA-ACL.
- Tornar os valores produzidos pelo simulador visiveis em `messages.csv`.

## Estado verificado no PADE novo
- O arquivo principal e `agent_example_1_mosaik_updated.py`.
- O agente encapsula os dados do Mosaik em mensagens `INFORM` para si mesmo, usando ontologia `mosaik_data`.
- O conteudo e serializado em JSON antes de ser enviado para a rede PADE.
- Os logs atualmente presentes na pasta mostram leituras sucessivas de `val_out` com os valores `2001`, `4002`, `6003` e `8004`.

## Ajustes consolidados
- A integracao foi adaptada para a API 3.0 do Mosaik.
- O registro dos dados deixou de depender de banco relacional e passou a usar a telemetria CSV do PADE novo.
- O payload gravado em `messages.csv` ficou legivel e filtravel por ontologia.
- Este exemplo ainda mantem uma inicializacao de sessao propria com `datetime.now()`, portanto ele nao esta tao alinhado ao runtime integrado quanto os exemplos basicos mais recentes.

## Logs esperados
- `sessions.csv`: sessoes com nome `Mosaik_FIPA_Logging`.
- `messages.csv`: mensagens `inform` com ontologia `mosaik_data` e payload JSON.
- Cada mensagem representa um snapshot de dados devolvido pelo simulador.

## Observacao
- Aqui o objetivo principal nao e a conversa entre agentes diferentes, e sim a auditoria dos dados do simulador dentro do formato ACL do PADE.
