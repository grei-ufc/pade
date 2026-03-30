Um momento Por Favor!
=====================

Com o PADE é possível adiar a execução de um trecho de código de forma
assíncrona e não bloqueante usando o método ``call_later()`` herdado
pela classe ``Agent``.

Como utilizar ``call_later()``
------------------------------

O método recebe:

* o tempo de atraso em segundos;
* o método que deve ser chamado depois desse atraso;
* opcionalmente os argumentos desse método.

Em outras palavras:

::

    self.call_later(tempo_em_segundos, metodo, *args)

Exemplo prático
---------------

No exemplo abaixo, o agente agenda ``say_hello()`` para ser executado
10 segundos após a inicialização:

::

    from pade.misc.utility import display_message, start_loop
    from pade.core.agent import Agent
    from pade.acl.aid import AID
    from pade.misc.data_logger import get_shared_session_id, logger
    from sys import argv


    class HelloAgent(Agent):
        def __init__(self, aid):
            super().__init__(aid=aid, debug=False)

        def on_start(self):
            super().on_start()
            self.call_later(10.0, self.say_hello)

        def say_hello(self):
            display_message(self.aid.localname, "Hello, I'm an agent from the future!")


    if __name__ == '__main__':
        ams_config = {'name': 'localhost', 'port': 8000}
        session_id = get_shared_session_id()

        logger.log_session(
            session_id=session_id,
            name=f"CallLater_{session_id}",
            state='Started'
        )

        port = int(argv[1]) if len(argv) > 1 else 20000
        hello_agent = HelloAgent(AID(name=f'hello_agent@localhost:{port}'))
        hello_agent.update_ams(ams_config)

        start_loop([hello_agent])

Esse agendamento não trava o reactor do Twisted. O agente continua
respondendo à infraestrutura do PADE enquanto aguarda o momento de
executar ``say_hello()``.

``call_later()`` x ``call_in_thread()``
---------------------------------------

Use ``call_later()`` quando a função a ser chamada for rápida e não
bloqueante.

Se a função fizer algo bloqueante, como ``time.sleep()``, acesso pesado
ao disco ou uma rotina demorada de cálculo, prefira ``call_in_thread()``.
Esse padrão aparece no
``pade/tests/agent_example_6/agent_example_6_updated.py``, onde a
função bloqueante roda em paralelo sem interromper as publicações do
protocolo ``FIPA-Subscribe``.
