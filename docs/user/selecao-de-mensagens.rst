Seleção de Mensagens
====================

Com PADE é possível implementar filtros de mensagens de maneira simples e direta, por meio da classe Filtro:

::

    from pade.acl.filters import Filter

Filtrando mensagens com o módulo filters
----------------------------------------

Por exemplo para a seguinte mensagem:

::

    from pade.acl.messages import ACLMessage
    from pade.acl.aid import AID

    message = ACLMessage(ACLMessage.INFORM)
    message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
    message.set_sender(AID('remetente'))
    message.add_receiver(AID('destinatario'))


Podemos criar o seguinte filtro:

::

    from pade.acl.filters import Filter

    f.performative = ACLMessage.REQUEST


Em uma sessão IPython é possível observar o efeito da aplicação do filtro sobre a mensagem:

::

    >> f.filter(message)
    >> False


Ajustando agora o filtro para outra condição:

::

    f.performative = ACLMessage.INFORM

E aplicando o filtro novamente sobre a mensagem, obtemos um novo resultado:

.. sourcecode:: ipython

    >> f.filter(message)
    >> True
    
