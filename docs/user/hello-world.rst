.. _hello-world-page:

Alô Mundo
---------

O primeiro passo com o PADE continua sendo simples: definir agentes,
registrá-los no AMS e iniciar o loop de execução.

No PADE novo, a pasta ``pade/tests/hello_world`` contém duas versões do
mesmo exemplo:

* ``hello_world_minimal.py``: versão mínima, feita para imprimir apenas
  no terminal;
* ``hello_world.py``: versão com tráfego ACL real, feita para também
  preencher ``messages.csv``.

Versão mínima
~~~~~~~~~~~~~

Se a ideia for só validar a instalação e ver o agente subir, comece por
``hello_world_minimal.py``:

::

    from pade.acl.aid import AID
    from pade.core.agent import Agent
    from pade.misc.utility import display_message, start_loop
    from sys import argv


    class HelloWorldAgent(Agent):
        def __init__(self, aid):
            super().__init__(aid=aid, debug=False)

        def on_start(self):
            super().on_start()
            display_message(self.aid.localname, 'Hello World!')


    if __name__ == '__main__':
        ams_config = {'name': 'localhost', 'port': 8000}
        base_port = int(argv[1]) if len(argv) > 1 else 20000
        agent = HelloWorldAgent(AID(name=f'hello_agent_{base_port}@localhost:{base_port}'))
        agent.update_ams(ams_config)

        start_loop([agent])

Essa versão é a mais curta e serve para mostrar o método simples de
imprimir no terminal. Se você executá-la com ``pade start-runtime``, o
runtime ainda criará ``sessions.csv``, ``agents.csv`` e ``events.csv``,
mas ``messages.csv`` continuará vazio porque nenhuma mensagem ACL foi
trocada.

Versão com logging de mensagens
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Se você quiser demonstrar o Sniffer e ver uma linha real em
``messages.csv``, use ``hello_world.py``:

::

    from pade.acl.messages import ACLMessage
    from pade.acl.aid import AID
    from pade.core.agent import Agent
    from pade.misc.data_logger import get_shared_session_id, logger
    from pade.misc.utility import display_message, start_loop
    from sys import argv


    class HelloReceiverAgent(Agent):
        def __init__(self, aid):
            super().__init__(aid=aid, debug=False)

        def on_start(self):
            super().on_start()
            display_message(self.aid.localname, 'Hello World! Receiver online.')

        def react(self, message):
            super().react(message)

            if message.ontology != 'hello_world_ontology':
                return

            display_message(
                self.aid.localname,
                f'Received message: {message.content}'
            )


    class HelloSenderAgent(Agent):
        def __init__(self, aid, receiver_aid):
            super().__init__(aid=aid, debug=False)
            self.receiver_aid = receiver_aid

        def on_start(self):
            super().on_start()
            display_message(self.aid.localname, 'Hello World! Sender online.')
            self.call_later(2.0, self.send_hello_world_message)

        def send_hello_world_message(self):
            message = ACLMessage(ACLMessage.INFORM)
            message.add_receiver(self.receiver_aid)
            message.set_ontology('hello_world_ontology')
            message.set_content('Hello World Message!')
            self.send(message)


    if __name__ == '__main__':
        ams_config = {'name': 'localhost', 'port': 8000}
        session_id = get_shared_session_id()

        logger.log_session(
            session_id=session_id,
            name=f"HelloWorld_{session_id}",
            state='Started'
        )

        base_port = int(argv[1]) if len(argv) > 1 else 20000
        receiver_port = base_port
        sender_port = base_port + 1000

        receiver_aid = AID(name=f'hello_receiver_{receiver_port}@localhost:{receiver_port}')
        sender_aid = AID(name=f'hello_sender_{sender_port}@localhost:{sender_port}')

        receiver_agent = HelloReceiverAgent(receiver_aid)
        sender_agent = HelloSenderAgent(sender_aid, receiver_aid)

        for agent in (receiver_agent, sender_agent):
            agent.update_ams(ams_config)

        start_loop([receiver_agent, sender_agent])

Executando a simulação
----------------------

No terminal, execute da forma que fizer mais sentido para o seu
diretório atual.

Para a versão mínima:

.. code-block:: console

    $ pade start-runtime --port 20000 pade/tests/hello_world/hello_world_minimal.py

ou, se você já estiver dentro da pasta do exemplo:

.. code-block:: console

    $ cd pade/tests/hello_world
    $ pade start-runtime --port 20000 hello_world_minimal.py

Para a versão com logging de mensagens:

.. code-block:: console

    $ pade start-runtime --port 20000 pade/tests/hello_world/hello_world.py

Se tudo estiver correto, o PADE iniciará o AMS, o Sniffer e o seu
script. Na versão mínima, você verá apenas o ``Hello World!`` no
terminal. Na versão com logging, verá também a entrada do agente
destinatário, a entrada do agente remetente e o envio da mensagem
``Hello World Message!``.

.. image:: ../img/pade_splash_screen.png
    :align: center
    :width: 8.0in

Sobre os logs
-------------

Na versão mínima, o runtime ainda gera ``sessions.csv``, ``agents.csv``
e ``events.csv``, mas ``messages.csv`` fica sem entradas porque o
exemplo não troca mensagens ACL.

Na versão com logging, o agente remetente envia uma mensagem ACL real
para outro agente, então o Sniffer consegue interceptar o tráfego e
persistir pelo menos uma linha em ``messages.csv``.

Modo manual
-----------

O fluxo integrado com ``start-runtime`` é o recomendado, mas você ainda
pode subir os componentes separadamente quando estiver depurando a
infraestrutura:

.. code-block:: console

    $ python -m pade.core.new_ams user user@pade.com 12345 8000

.. code-block:: console

    $ python -m pade.core.sniffer 8001

.. code-block:: console

    $ python hello_world_minimal.py 20000

ou, se você quiser a versão com logging de mensagens:

.. code-block:: console

    $ python hello_world.py 20000

Esses dois arquivos cobrem bem as duas primeiras etapas do onboarding:
primeiro imprimir no terminal, depois trocar uma mensagem ACL real. O
passo seguinte costuma ser adicionar um comportamento temporal ou
expandir a conversa para respostas, filtros e protocolos FIPA.
