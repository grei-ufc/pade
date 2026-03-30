# Changelog - agent_example_5

## Objetivo atual
- Demonstrar o protocolo FIPA Subscribe com um publicador e dois assinantes.
- Validar o atraso proposital antes das assinaturas e o fluxo continuo de publicacoes.

## Estado verificado no PADE novo
- O arquivo principal e `agent_example_5_updated.py`.
- A execucao recomendada e `pade start-runtime --port 24000 agent_example_5_updated.py`.
- O exemplo usa uma sessao compartilhada do runtime.
- Os assinantes aguardam alguns segundos antes de enviar `SUBSCRIBE`, entao as primeiras publicacoes podem ocorrer sem assinantes ativos.

## Ajustes consolidados
- O changelog antigo acumulava historico de outros exemplos e informacoes ja ultrapassadas.
- O exemplo atual registra corretamente `subscribe`, `agree` e `inform` em CSV.
- O comportamento esperado agora esta descrito com base no fluxo real do script.
- A documentacao foi ajustada para deixar claro que `messages.csv` nao fica vazio neste exemplo.

## Logs esperados
- `messages.csv`: `2 subscribe`, `2 agree` e varias mensagens `inform`.
- `agents.csv`: sniffer, um publicador e dois assinantes.
- `events.csv`: inicio do teste, publicacoes iniciais sem assinantes, envio das assinaturas, aceite das assinaturas e recebimento continuo das publicacoes.

## Observacao
- Ver algumas publicacoes antes do `SUBSCRIBE` ser aceito e normal neste exemplo, porque esse atraso faz parte do desenho didatico do teste.
