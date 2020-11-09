Enviando Mensagens
==================

Para enviar uma mensagem com o PADE é muito simples! As mensagens enviadas pelos agentes desenvolvidos com PADE seguem o padrão FIPA-ACL e têm os seguintes campos:

* *conversation-id:* identidade única de uma conversa;
* *performative:* rótulo da mensagem;
* *sender:* remetente da mensagem;
* *receivers:* destinatários da mensagem;
* *content:* conteúdo da mensagem;
* *protocol:* protocolo da mensagem;
* *language:* linguagem utilizada;
* *encoding:* codificação da mensagem;
* *ontology:* ontologia utilizada;
* *reply-with:* Expressão utilizada pelo agente de resposta a identificar a mensagem;
* *reply-by:* A referência a uma ação anterior em que a mensagem é uma resposta;
* *in-reply-to:* Data/hora indicando quando uma resposta deve ser recebida..

Mensagens FIPA-ACL no PADE
--------------------------

Uma mensagem FIPA-ACL pode ser montada no pade da seguinte forma:

::

    from pade.acl.messages import ACLMessage, AID
    message = ACLMessage(ACLMessage.INFORM)
    message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
    message.add_receiver(AID('agente_destino'))
    message.set_content('Ola Agente')


Enviando uma mensagem com PADE
------------------------------

Uma vez que se está dentro de uma instância da classe `Agent()` a mensagem pode ser enviada, simplesmente utilizando o comando:

::

    self.send(message)


Mensagem no padrão FIPA-ACL
---------------------------

Realizando o comando `print message` a mensagem no padão FIPA ACL será impressa na tela:

::

    (inform
        :conversationID b2e806b8-50a0-11e5-b3b6-e8b1fc5c3cdf
        :receiver
            (set
                (agent-identifier
                    :name agente_destino@localhost:51645
                    :addresses 
                        (sequence
                        localhost:51645
                        )
                )

            )
        :content "Ola Agente"
        :protocol fipa-request protocol
    )


Mensagem no padrão XML
----------------------

Mas também é possível obter a mensagem no formato XML por meio do comando `print message.as_xml()`

.. code-block:: xml

    <?xml version="1.0" ?>
    <ACLMessage date="01/09/2015 as 08:58:03:113891">
            <performative>inform</performative>
            <sender/>
            <receivers>
                    <receiver>agente_destino@localhost:51645</receiver>
            </receivers>
            <reply-to/>
            <content>Ola Agente</content>
            <language/>
            <encoding/>
            <ontology/>
            <protocol>fipa-request protocol</protocol>
            <conversationID>b2e806b8-50a0-11e5-b3b6-e8b1fc5c3cdf</conversationID>
            <reply-with/>
            <in-reply-to/>
            <reply-by/>
    </ACLMessage>
