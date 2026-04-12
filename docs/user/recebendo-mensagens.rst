Recebendo Mensagens
===================

No PADE, quando você quer tratar mensagens ACL fora de um protocolo
específico, o ponto de extensão mais comum é o método ``react()`` da
classe ``Agent``.

Recebendo mensagens FIPA-ACL com ``react()``
--------------------------------------------

O exemplo abaixo mostra dois agentes: um remetente, que agenda o envio
de uma mensagem, e um destinatário, que sobrescreve ``react()`` para
tratar o recebimento.

::

    from pade.misc.utility import display_message, start_loop
    from pade.core.agent import Agent
    from pade.acl.messages import ACLMessage
    from pade.acl.aid import AID
    from pade.misc.data_logger import get_shared_session_id, logger
    from sys import argv


    class Remetente(Agent):
        def __init__(self, aid, target_aid):
            super().__init__(aid=aid, debug=False)
            self.target_aid = target_aid

        def on_start(self):
            super().on_start()
            display_message(self.aid.localname, 'Enviando mensagem...')
            self.call_later(8.0, self.sending_message)

        def sending_message(self):
            message = ACLMessage(ACLMessage.INFORM)
            message.add_receiver(AID(name=self.target_aid))
            message.set_ontology('saudacao')
            message.set_content('Ola Destinatario!')
            self.send(message)


    class Destinatario(Agent):
        def __init__(self, aid):
            super().__init__(aid=aid, debug=False)

        def react(self, message):
            super().react(message)
            display_message(
                self.aid.localname,
                f'Mensagem recebida de {message.sender.name}'
            )


    if __name__ == '__main__':
        ams_config = {'name': 'localhost', 'port': 8000}
        session_id = get_shared_session_id()

        logger.log_session(
            session_id=session_id,
            name=f"React_{session_id}",
            state='Started'
        )

        agents = []
        base_port = int(argv[1]) if len(argv) > 1 else 20000

        destinatario_name = f'destinatario@localhost:{base_port}'
        destinatario = Destinatario(AID(name=destinatario_name))
        destinatario.update_ams(ams_config)
        agents.append(destinatario)

        remetente_port = base_port + 1
        remetente = Remetente(
            AID(name=f'remetente@localhost:{remetente_port}'),
            destinatario_name
        )
        remetente.update_ams(ams_config)
        agents.append(remetente)

        start_loop(agents)

Executando o exemplo
--------------------

O fluxo recomendado é:

.. code-block:: console

    $ pade start-runtime --port 20000 meu_exemplo.py

Depois da inicialização dos agentes, o remetente aguardará 8 segundos e
enviará a mensagem ao destinatário. O método ``react()`` do destinatário
será chamado quando a mensagem chegar.

Visualização dos registros
--------------------------

Com o Sniffer ativo, a troca ficará registrada em ``logs/messages.csv``.
Você poderá verificar:

* o ``performative`` da mensagem;
* o remetente e o destinatário;
* o conteúdo enviado;
* a ontologia, se definida.

Quando usar ``react()``
-----------------------

``react()`` é especialmente útil quando:

* você quer tratar mensagens fora de um protocolo FIPA formal;
* precisa implementar lógica direta de recebimento;
* deseja inspecionar ACLs recebidas antes de adicionar comportamentos
  mais elaborados.

Se a conversa seguir um padrão FIPA conhecido, como ``REQUEST`` ou
``SUBSCRIBE``, normalmente vale mais a pena usar os protocolos prontos
em ``pade.behaviours.protocols``.
