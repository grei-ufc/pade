Agentes Temporais
=================

Em aplicações reais é comum que o comportamento do agente seja
executado de tempos em tempos, e não apenas uma vez. No PADE isso é
feito com a classe ``TimedBehaviour``.

Execução de um agente temporal
------------------------------

O exemplo clássico desse padrão está no arquivo
``pade/tests/agent_example_2/agent_example_2_updated.py``. A ideia é
simples: criar um comportamento que execute ``on_time()`` em intervalos
regulares.

::

    from pade.misc.utility import display_message, start_loop
    from pade.core.agent import Agent
    from pade.acl.aid import AID
    from pade.behaviours.protocols import TimedBehaviour
    from pade.misc.data_logger import get_shared_session_id, logger
    from sys import argv


    class ComportTemporal(TimedBehaviour):
        def __init__(self, agent, time):
            super().__init__(agent, time)

        def on_time(self):
            super().on_time()
            display_message(self.agent.aid.localname, 'Hello World!')


    class AgenteHelloWorld(Agent):
        def __init__(self, aid, session_id):
            super().__init__(aid=aid, debug=False)
            self.session_id = session_id

            comp_temp = ComportTemporal(self, 1.0)
            self.behaviours.append(comp_temp)

        def on_start(self):
            super().on_start()
            logger.log_agent(
                agent_id=self.aid.name,
                session_id=self.session_id,
                name=self.aid.name,
                state='Active'
            )


    if __name__ == '__main__':
        ams_config = {'name': 'localhost', 'port': 8000}
        session_id = get_shared_session_id()

        logger.log_session(
            session_id=session_id,
            name=f"TimedHelloWorld_{session_id}",
            state='Started'
        )

        agents = []
        base_port = int(argv[1]) if len(argv) > 1 else 20000

        for offset in (0, 1000):
            port = base_port + offset
            name = f'agent_hello_{port}@localhost:{port}'
            agent = AgenteHelloWorld(AID(name=name), session_id)
            agent.update_ams(ams_config)
            agents.append(agent)

        start_loop(agents)

O comportamento ``TimedBehaviour`` recebe o agente e o intervalo em
segundos. Sempre que o tempo expira, o método ``on_time()`` é chamado.

Executando o exemplo
--------------------

O fluxo recomendado é:

.. code-block:: console

    $ pade start-runtime --port 20000 pade/tests/agent_example_2/agent_example_2_updated.py

Ao executar esse exemplo, o terminal exibirá periodicamente
``Hello World!`` para cada agente. Ao mesmo tempo, a pasta ``logs/``
registrará a sessão, os agentes ativos e os eventos temporais do teste.

Quando usar ``TimedBehaviour``
------------------------------

Esse comportamento é útil sempre que um agente precisar:

* publicar dados periodicamente;
* consultar outro agente em intervalos regulares;
* verificar estados locais da simulação;
* acionar rotinas cíclicas sem bloquear o reactor.

Se a tarefa for bloqueante, como ``sleep()``, acesso pesado a disco ou
processamento longo, prefira usar ``call_in_thread()``. Esse padrão é
mostrado no ``agent_example_6_updated.py``.
