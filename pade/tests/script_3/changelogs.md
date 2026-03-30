# Changelog - script_3

## Objetivo atual
- Demonstrar um fluxo minimo de FIPA Request no formato `REQUEST -> AGREE -> INFORM`.
- Manter o exemplo simples e totalmente observavel pelos logs CSV.

## Estado verificado no PADE novo
- O arquivo principal e `script_3_updated.py`.
- A execucao recomendada e `pade start-runtime --port 24000 script_3_updated.py`.
- O participante recebe um `REQUEST`, responde com `AGREE` e depois conclui com `INFORM`.
- O arquivo legado equivalente esta quebrado sintaticamente; a referencia valida desta migracao e a versao nova.

## Ajustes consolidados
- O script passou a usar `get_shared_session_id()`.
- Os AIDs ficaram deterministas a partir da porta base do runtime.
- O receptor do `REQUEST` passou a usar o nome completo do participante, evitando inconsistencias em `events.csv`.
- O texto, comentarios e mensagens de terminal foram mantidos em ingles para padronizacao do material novo.

## Logs esperados
- `messages.csv`: exatamente `1 request`, `1 agree` e `1 inform`.
- `agents.csv`: sniffer, um participante e um iniciador.
- `events.csv`: `message_sent`, `message_received` e `message_stored` para as tres etapas do protocolo.

## Observacao
- Este e um exemplo de conversa unica. O runtime continua ativo, mas o protocolo de aplicacao termina apos a terceira mensagem.
