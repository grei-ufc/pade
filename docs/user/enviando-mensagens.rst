Enviando Mensagens
==================

Enviar uma mensagem com o PADE é simples: os agentes trocam mensagens no
padrão FIPA-ACL, representadas pela classe ``ACLMessage``.

Os campos mais utilizados são:

* ``conversation-id``: identificador único da conversa;
* ``performative``: rótulo da mensagem, como ``INFORM`` ou ``REQUEST``;
* ``sender``: remetente da mensagem;
* ``receivers``: destinatários da mensagem;
* ``content``: conteúdo transmitido;
* ``protocol``: protocolo associado à conversa;
* ``language``: linguagem utilizada;
* ``encoding``: codificação declarada;
* ``ontology``: ontologia da mensagem, muito útil para filtros e análise
  em ``messages.csv``;
* ``reply-with``: identificador criado pelo emissor para que a próxima
  resposta possa referenciar a mensagem atual;
* ``in-reply-to``: campo usado pelo receptor para apontar a qual
  mensagem está respondendo;
* ``reply-by``: prazo esperado para recebimento da resposta.

Montando uma mensagem FIPA-ACL
------------------------------

Uma mensagem ACL pode ser criada assim:

::

    from pade.acl.messages import ACLMessage
    from pade.acl.aid import AID

    message = ACLMessage(ACLMessage.INFORM)
    message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
    message.add_receiver(AID(name='agente_destino@localhost:20001'))
    message.set_ontology('saudacao')
    message.set_content('Ola Agente')

Se necessário, você também pode preencher campos de correlação:

::

    message.set_reply_with('msg-001')
    message.set_reply_by('2026-03-27T18:00:00')

Enviando a mensagem
-------------------

Uma vez dentro de uma instância de ``Agent``, a mensagem é enviada com:

::

    self.send(message)

Esse é o mesmo mecanismo utilizado nos exemplos de ``FIPA-Request``,
``FIPA-Contract-Net`` e ``FIPA-Subscribe``.

Representação ACL em texto
--------------------------

O objeto ``ACLMessage`` ainda implementa a representação textual no
formato ACL. Basta imprimir a mensagem:

::

    print(message)

Saída típica:

::

    (inform
    :conversationID 6f2f6e24-5c7f-11ef-a9f6-0242ac120002
    :receiver
     (set
    (agent-identifier
    :name agente_destino@localhost:20001
    :addresses
    (sequence
    localhost:20001
    )
    )
    )
    :content "Ola Agente"
    :protocol fipa-request protocol
    :ontology saudacao
    )

Representação XML
-----------------

Também é possível obter a mensagem em XML:

::

    print(message.as_xml())

Exemplo de saída:

.. code-block:: xml

    <?xml version="1.0" ?>
    <ACLMessage>
      <performative>inform</performative>
      <sender />
      <receivers>
        <receiver>agente_destino@localhost:20001</receiver>
      </receivers>
      <content>Ola Agente</content>
      <ontology>saudacao</ontology>
      <protocol>fipa-request protocol</protocol>
      <conversationID>6f2f6e24-5c7f-11ef-a9f6-0242ac120002</conversationID>
    </ACLMessage>

Mensagens nos logs CSV
----------------------

Quando o Sniffer está ativo, as mensagens trocadas passam a ser gravadas
em ``logs/messages.csv``. Ali você encontrará, entre outras colunas:

* ``message_id``;
* ``conversation_id``;
* ``performative``;
* ``protocol``;
* ``sender``;
* ``receivers``;
* ``content``;
* ``ontology``.

Isso torna muito mais simples filtrar interações por protocolo,
ontologia ou agente com ferramentas como Pandas, Excel ou Power BI.
