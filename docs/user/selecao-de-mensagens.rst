Seleção de Mensagens
====================

Com o PADE é possível implementar filtros de mensagens de forma simples
por meio da classe ``Filter``. Isso é especialmente útil quando o método
``react()`` precisa tratar apenas um subconjunto das ACLs recebidas.

::

    from pade.acl.filters import Filter

Filtrando mensagens
-------------------

Considere a seguinte mensagem:

::

    from pade.acl.messages import ACLMessage
    from pade.acl.aid import AID

    message = ACLMessage(ACLMessage.INFORM)
    message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
    message.set_sender(AID(name='remetente'))
    message.add_receiver(AID(name='destinatario'))

Agora crie um filtro:

::

    from pade.acl.filters import Filter

    f = Filter()
    f.performative = ACLMessage.REQUEST

Ao aplicar o filtro:

.. code-block:: python

    >> f.filter(message)
    False

Se ajustarmos o critério para coincidir com a mensagem:

.. code-block:: python

    f.performative = ACLMessage.INFORM

E filtrarmos novamente:

.. code-block:: python

    >> f.filter(message)
    True

Esse mecanismo pode ser combinado com ``protocol``, ``sender`` e outros
campos da ACL para criar regras mais específicas de roteamento dentro do
agente.
