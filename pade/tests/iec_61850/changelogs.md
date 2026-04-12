# Changelog - iec_61850

## Objetivo atual
- Demonstrar uma integracao entre agentes PADE e um IED IEC 61850.
- Disparar requisicoes periodicas de controle e registrar o retorno no formato FIPA Request.

## Estado verificado no PADE novo
- O arquivo principal e `agent_example_iec_61850_1_updated.py`.
- Dois `RequestAgent` enviam `REQUEST` periodicos para dois `IEC61850Agent`.
- Cada agente IEC 61850 tenta executar a rotina de leitura e escrita no IED e responde com `INFORM`.
- Os logs atuais da pasta mostram repeticao do ciclo `request -> inform` aproximadamente a cada 10 segundos.

## Ajustes consolidados
- A integracao foi portada para Python 3.12 com a biblioteca `pyiec61850`.
- O registro em CSV substituiu o armazenamento legado em banco relacional.
- O exemplo agora usa `get_shared_session_id()` para alinhar a sessao do exemplo com a sessao do runtime integrado.
- O script falha com uma mensagem clara quando `pyiec61850` nao estiver instalado no ambiente ativo.
- A pasta agora inclui um `README.md` com o fluxo recomendado de execucao em dois terminais.

## Logs esperados
- `sessions.csv`: sessao com nome `IEC61850_Integration`.
- `messages.csv`: repeticao de mensagens `request` e `inform` usando o protocolo `fipa-request protocol`.
- `agents.csv`: dois agentes IEC 61850, dois agentes requisitantes e o sniffer, quando a execucao estiver completa.

## Observacao
- Este exemplo depende de um ambiente IEC 61850 disponivel. O foco da migracao aqui foi a compatibilidade do fluxo e da auditoria, nao a remocao dessa dependencia externa.
- A dependencia `pyiec61850` nao faz parte do nucleo do PADE e deve ser instalada separadamente, ou via extra opcional `pade[iec61850]`.
