# Changelog - script_5

## Objetivo atual
- Demonstrar a menor troca ACL possivel entre dois agentes.
- Diferenciar claramente mensagens de aplicacao de mensagens internas de infraestrutura.

## Estado verificado no PADE novo
- O arquivo principal e `script_5_updated.py`.
- A execucao recomendada e `pade start-runtime --port 24000 script_5_updated.py`.
- Bob envia um unico `INFORM` para Alice com o conteudo `Hello Alice!`.
- O runtime pode continuar aberto exibindo verificacoes de conexao, mas isso nao significa que a conversa de aplicacao esta se repetindo.

## Ajustes consolidados
- O script passou a usar `get_shared_session_id()` e AIDs deterministas.
- O terminal foi filtrado para ignorar `Agent successfully identified.`, `CONNECTION` e mensagens de tabela do AMS.
- O comportamento atual esta alinhado ao objetivo historico do exemplo: uma unica saudacao ACL.
- O changelog anterior foi corrigido para deixar claro que `messages.csv` conter apenas uma linha e o esperado.

## Logs esperados
- `messages.csv`: exatamente `1 inform`, com conteudo `Hello Alice!`.
- `agents.csv`: sniffer, Alice e Bob.
- `events.csv`: uma unica troca de aplicacao, alem dos eventos de infraestrutura do runtime.

## Observacao
- As mensagens `CONNECTION` vistas no terminal nao entram em `messages.csv` porque nao pertencem a conversa ACL da aplicacao.
