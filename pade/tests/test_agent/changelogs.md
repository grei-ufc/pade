# Changelog - test_agent

## Objetivo atual
- Validar uma troca simples entre dois agentes de teste.
- Permanecer o mais proximo possivel da intencao do exemplo legado, sem introduzir repeticao indevida.

## Estado verificado no PADE novo
- O arquivo principal e `test_agent_updated.py`.
- A execucao recomendada e `pade start-runtime --port 24000 test_agent_updated.py`.
- O initiator envia uma unica mensagem `Hello Agent!` apos um atraso curto.
- O participant responde uma unica vez com `Hello to you too, Agent!`.
- O runtime continua ativo depois disso, mas a conversa ACL nao entra em loop.

## Ajustes consolidados
- O envio recorrente por `TimedBehaviour` foi removido porque nao refletia o comportamento desejado do exemplo legado.
- O script passou a usar `call_later(3.0, ...)` para disparo unico.
- A sessao passou a usar `get_shared_session_id()` e AIDs deterministas.
- O terminal agora ignora mensagens de infraestrutura ruidosas para destacar apenas a conversa de aplicacao.

## Logs esperados
- `messages.csv`: exatamente `2 inform`, uma de ida e uma de resposta.
- `agents.csv`: sniffer, initiator e participant.
- `events.csv`: uma unica troca `message_sent -> message_received -> message_stored` para cada lado da conversa.

## Observacao
- O runtime nao precisa encerrar automaticamente. O importante aqui e que o protocolo da aplicacao aconteca uma vez, como no desenho do exemplo legado.
