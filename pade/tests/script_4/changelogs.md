# Changelog - script_4

## Objetivo atual
- Simular uma recomposicao de energia usando FIPA Contract Net.
- Registrar propostas de potencia com payload legivel e portas deterministicas.

## Estado verificado no PADE novo
- O arquivo principal e `script_4_updated.py`.
- A execucao recomendada e `pade start-runtime --port 24000 script_4_updated.py`.
- O iniciador envia um `CFP` para dois participantes, compara as propostas de potencia, aceita a melhor e recebe um `INFORM` de confirmacao.
- O fluxo atual esta coerente entre terminal, `messages.csv` e `events.csv`.

## Ajustes consolidados
- O conteudo das mensagens foi migrado de `pickle` para JSON.
- A sessao do exemplo passou a usar `get_shared_session_id()`.
- Os AIDs dos agentes passaram a ser derivados da porta base do runtime.
- O changelog anterior desta pasta foi substituido porque ainda documentava payload binario e comportamentos ja corrigidos.

## Logs esperados
- `messages.csv`: `2 cfp`, `2 propose`, `1 reject-proposal`, `1 accept-proposal` e `1 inform`.
- O `content` deve ficar legivel em JSON, por exemplo `{"type": "recomposition_order", "qty": 100.0}` e `{"value": 200.0}`.
- `agents.csv`: sniffer, dois participantes e um iniciador.

## Observacao
- Este exemplo ja esta no mesmo padrao tecnico de `script_2` e `script_3`: sessao compartilhada, logs legiveis e AIDs estaveis.
