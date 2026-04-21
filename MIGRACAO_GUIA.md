# Guia de Migracao do PADE legado para o PADE em Python 3.12

Este documento resume o que foi efetivamente confirmado no código atual de `NOVO/pade` durante a migração para Python 3.12. O foco aqui não e repetir todo o histórico do projeto, mas registrar com precisão como a arquitetura funciona hoje, quais padrões foram adotados nos exemplos e quais diferenças ainda restam em alguns casos especializados.

## Escopo

- Base analisada: `NOVO/pade`
- Versão do pacote observada em `pyproject.toml`: `3.0`
- Fluxo de execução recomendado: `pade start-runtime --port <porta> <arquivo.py>`
- Persistência de telemetria: CSV (`sessions.csv`, `agents.csv`, `messages.csv`, `events.csv`)

## Resumo executivo

- O fluxo principal do PADE novo deixou de depender de Flask e SQLite.
- O comando de uso diario e `pade start-runtime`, que orquestra AMS, Sniffer e scripts de agentes.
- O runtime cria uma sessao compartilhada via variavel de ambiente `PADE_SESSION_ID`.
- O onboarding agora ficou dividido em dois Hello Worlds na pasta `pade/tests/hello_world`:
  - `hello_world_minimal.py` para terminal e logs basicos;
  - `hello_world.py` para terminal + uma mensagem ACL real observavel em `messages.csv`.
- Os exemplos mais recentes foram migrados para usar `get_shared_session_id()` e AIDs completos no formato `agente@localhost:porta`.
- `messages.csv` e escrito pelo Sniffer, nao por `agent.py`.
- `agent.py` registra eventos como `message_sent` e `message_received` em `events.csv`.

## Correcoes importantes em relacao a versoes anteriores deste guia

- O registro de `messages.csv` nao esta embutido diretamente em `react()` ou `send()` de `pade/core/agent.py`. O escritor canonico de `messages.csv` e `pade/core/sniffer.py`.
- O comando atual do CLI e `start-runtime`, com hifen. A forma com underscore nao corresponde ao nome do comando visivel ao usuario.
- O padrao atual do projeto e o runtime integrado. Fluxos manuais com inicializacao separada de AMS aparecem apenas em casos especificos ou historicos.
- `messages.csv` e `events.csv` nao possuem coluna `session_id`. A correlacao entre execucoes depende da limpeza da pasta `logs/`, do contexto temporal ou da leitura conjunta de `sessions.csv` e `agents.csv`.

## Mudancas confirmadas por arquivo

## `pyproject.toml`

- A versao do pacote esta em `3.0`.
- Os metadados de empacotamento agora ficam centralizados na tabela PEP 621 `project`.
- O script de console `pade` e declarado em `project.scripts`.
- O backend de build e `setuptools.build_meta`, mantendo compatibilidade com o fluxo moderno via `uv`.

Leitura pratica:

- O empacotamento atual esta orientado a runtime leve e telemetria CSV.
- O ecossistema web legado nao faz parte do fluxo padrao de instalacao e uso.

## `pade/cli/pade_cmd.py`

- O comando principal e `pade start-runtime`.
- O CLI chama `init_data_logger(config)` antes de subir os processos.
- `init_data_logger(config)` cria a sessao inicial `Session_<id>`, registra `runtime_started` em `events.csv` e define `PADE_SESSION_ID`.
- O CLI sobe AMS e Sniffer como subprocessos e depois executa os scripts de agentes, repassando a porta base como argumento.
- O runtime integrado agora suporta `--detailed`, alem do alias `start-runtime-detailed`.
- Comandos utilitarios atuais: `show-logs`, `export-logs`, `version` e `clean-logs`.

Leitura pratica:

- O `start-runtime` e o equivalente moderno do fluxo integrado que o usuario esperava do PADE legado.
- `start-runtime --detailed` e `start-runtime-detailed` mantem o mesmo fluxo de execucao, mas recolocam no terminal os rastros tecnicos de AMS e Sniffer.
- A arquitetura interna continua desacoplada, mas a experiencia de uso voltou a ser centralizada.

## `pade/misc/data_logger.py`

- O modulo define `get_shared_session_id(default=None)`.
- O diretorio de logs agora e resolvido em caminho absoluto para evitar falhas quando subprocessos mudam de contexto de execucao.
- Se `PADE_SESSION_ID` existir, ela passa a ser a sessao dominante do runtime.
- Sao mantidos quatro arquivos CSV:
  - `sessions.csv`
  - `agents.csv`
  - `messages.csv`
  - `events.csv`
- `agents.csv` usa upsert por par `(agent_id, session_id)`, evitando duplicacao do mesmo agente na mesma execucao.
- `messages.csv` guarda metadados ACL e o `content` convertido para string.
- `events.csv` guarda eventos livres do runtime e dos exemplos.

Leitura pratica:

- Para alinhar exemplos ao runtime integrado, o padrao recomendado e chamar `get_shared_session_id()` ao criar a sessao do exemplo.
- Isso tambem explica a diferenca entre os dois Hello Worlds:
  - o minimal nao envia mensagem ACL, entao `messages.csv` fica vazio;
  - o variante com logging envia um `INFORM` real, entao o Sniffer persiste a mensagem.

## `pade/core/new_ams.py`

- O AMS atual usa a sessao compartilhada do runtime.
- O proprio AMS registra `AMS_Session_<id>` em `sessions.csv`.
- O AMS registra agentes em `agents.csv`.
- A propagacao da tabela de agentes continua sendo parte essencial do funcionamento da plataforma.
- O fluxo atual nao inicializa banco relacional nem sobe interface web.
- A saida padrao no terminal ficou mais limpa; os rastros detalhados do AMS agora ficam atras do modo `--detailed`.

Leitura pratica:

- O AMS hoje e um servico de roteamento e coordenacao, nao um componente acoplado a SQLite/Flask.

## `pade/core/agent.py`

- O arquivo registra eventos de envio e recebimento em `events.csv`.
- O codigo atual emite eventos como `message_sent` e `message_received`.
- O arquivo nao grava `messages.csv` diretamente.
- O uso de AIDs completos ajuda a manter roteamento e logs estaveis.

Leitura pratica:

- Quando um exemplo esta com `events.csv` correto, mas `messages.csv` estranho, a primeira verificacao deve ser no Sniffer e no payload da mensagem, nao no logger do `Agent`.

## `pade/core/sniffer.py`

- Este e o escritor canonico de `messages.csv`.
- O Sniffer intercepta mensagens, bufferiza por remetente e grava o resultado em CSV.
- O campo `receivers` e canonizado como string estavel.
- O Sniffer tambem registra `message_stored` em `events.csv`.

Leitura pratica:

- Quando o payload da aplicacao e texto ou JSON, `messages.csv` tende a ficar legivel.
- Quando o payload da aplicacao e binario ou serializado com `pickle`, o CSV pode conter representacoes pouco amigaveis. Por isso os exemplos migrados passaram a preferir JSON quando a legibilidade dos logs importa.

## `pade/behaviours/protocols.py`

- `TimedBehaviour` no PADE novo e recorrente por projeto.
- O metodo `on_time()` volta a se agendar com `reactor.callLater(self.time, self.on_time)`.

Leitura pratica:

- Se o objetivo for executar algo uma unica vez apos atraso, o padrao recomendado e `call_later(...)`.
- Se o objetivo for comportamento periodico, `TimedBehaviour` continua sendo a escolha certa.

Esse ponto foi decisivo para corrigir:

- `test_agent`, que nao deveria entrar em loop
- exemplos periodicos como `agent_example_2`, `agent_example_3` e `iec_61850`, que devem continuar recorrentes

## `pade/misc/common.py`

- `PadeSession` ainda existe como camada de compatibilidade.
- Ela registra sessao e eventos no logger CSV.
- Apesar disso, o caminho principal para o usuario final continua sendo o CLI integrado, nao a montagem manual de sessao.

Leitura pratica:

- `PadeSession` ainda pode ser util em cenarios especificos, mas nao e o padrao que a documentacao principal deve promover.

## `pade/drivers/mosaik_driver.py`

- O uso atual do driver foi confirmado indiretamente pelo exemplo `mosaik_example`.
- O exemplo migrado declara API `3.0` do Mosaik e opera com payloads JSON na telemetria ACL.

Leitura pratica:

- O caso Mosaik e mais especializado do que os exemplos basicos de protocolo.
- A validacao mais importante nesta rodada foi: os dados do simulador conseguem ser refletidos em `messages.csv` como mensagens ACL legiveis.

## Padroes de migracao que se provaram corretos nos exemplos

Os exemplos que ficaram mais estaveis no PADE novo convergiram para o mesmo conjunto de praticas:

- Rodar com `pade start-runtime --port ...`
- Usar `get_shared_session_id()` dentro do exemplo
- Criar AIDs completos, por exemplo `agent@localhost:24000`
- Usar JSON quando a leitura humana de `messages.csv` for importante
- Filtrar mensagens de sistema em `react()` quando o objetivo do exemplo for didatico
- Usar `call_later(...)` em vez de `TimedBehaviour` para disparos unicos

## Estado atual dos exemplos migrados

Ja ficaram coerentes com o padrao novo:

- `agent_example_1`
- `agent_example_2`
- `agent_example_3`
- `agent_example_4`
- `agent_example_5`
- `agent_example_6`
- `script_2`
- `script_3`
- `script_4`
- `script_5`
- `test_agent`
- `test_pingpong`
- `iec_61850`
- `power_systems`

Casos mais especializados, com alguma diferenca residual de estilo:

- `mosaik_example`

No momento, `mosaik_example` e o caso especializado que ainda usa inicializacao de sessao local com `datetime.now()` em vez de seguir integralmente o mesmo padrao com `get_shared_session_id()` adotado pelos exemplos basicos mais recentes.

## Limites e cuidados ao interpretar os logs

- A pasta `logs/` acumula execucoes, salvo quando limpa manualmente.
- `messages.csv` pode ser gravado alguns segundos depois do evento aparecer no terminal, porque o Sniffer bufferiza mensagens antes de persistir.
- `CONNECTION`, `Agent successfully identified.` e mensagens de tabela do AMS podem aparecer no terminal, mas nem sempre pertencem a conversa ACL principal do exemplo.
- Para comparacoes limpas entre execucoes, o ideal e limpar ou arquivar `logs/` antes de rodar novamente.

## Conclusao

A migracao para Python 3.12 consolidou um PADE mais leve, mais auditavel e mais previsivel para os exemplos didaticos. O ponto central da nova arquitetura e:

- CLI integrado para a experiencia do usuario
- AMS e Sniffer desacoplados internamente
- telemetria CSV como base de observabilidade
- sessao compartilhada do runtime como referencia de correlacao

Sempre que um novo exemplo for migrado, o caminho mais seguro e repetir o padrao que ja se mostrou robusto nos exemplos atualizados:

1. `pade start-runtime --port ...`
2. `get_shared_session_id()`
3. AIDs completos
4. payload legivel
5. logs conferidos em `sessions.csv`, `agents.csv`, `messages.csv` e `events.csv`
