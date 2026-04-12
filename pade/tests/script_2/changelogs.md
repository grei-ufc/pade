# Changelog - script_2

## Objetivo atual
- Demonstrar uma negociacao FIPA Contract Net entre um consumidor e tres livrarias.
- Garantir que os logs exibam mensagens legiveis e com portas deterministicas.

## Estado verificado no PADE novo
- O arquivo principal e `script_2_updated.py`.
- A execucao recomendada e `pade start-runtime --port 24000 script_2_updated.py`.
- O consumidor dispara um `CFP`, recebe tres propostas, seleciona a melhor oferta, rejeita as demais e finaliza a compra com `INFORM`.
- O arquivo legado equivalente esta quebrado sintaticamente; por isso a referencia executavel para a migracao e esta versao nova.

## Ajustes consolidados
- O payload da negociacao foi migrado de `pickle` para JSON para evitar conteudo hexadecimal em `messages.csv`.
- O script passou a usar `get_shared_session_id()` para alinhar a sessao do exemplo com a sessao do runtime.
- Os AIDs ficaram deterministas a partir da porta base do runtime.
- O fluxo terminal e os CSVs agora descrevem a mesma negociacao.

## Logs esperados
- `messages.csv`: `3 cfp`, `3 propose`, `1 accept-proposal`, `2 reject-proposal` e `1 inform`.
- `agents.csv`: sniffer, `Saraiva`, `Cultura`, `Nobel` e `Consumer`.
- O conteudo das mensagens deve aparecer em JSON legivel, nao em bytes serializados.

## Observacao
- Este exemplo ja esta no padrao recomendado para o PADE novo: runtime integrado, sessao compartilhada, portas estaveis e payload textual auditavel.
