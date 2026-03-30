# Hello world in PADE - Versão Python 3.12.11
#
# Criado por Lucas S Melo em 21 de julho de 2015 - Fortaleza, Ceará - Brasil
#
# Adaptado por Douglas Barros em 04 de março de 2026 - Fortaleza, Ceará - Brasil

from pade.misc.utility import display_message, start_loop, format_message_content
from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.misc.data_logger import get_shared_session_id, logger
from sys import argv

class AgenteHelloWorld(Agent):
    def __init__(self, aid, peer_aid, session_id):
        super().__init__(aid=aid, debug=False)  # debug=True para ver mensagens formatadas no react
        self.peer_aid = peer_aid
        self.session_id = session_id
        
        # OPÇÃO 1: Exibição APENAS no terminal local (NÃO é interceptado pelo Sniffer/messages.csv)
        display_message(self.aid.localname, 'Hello World! (Apenas Terminal)')
        
        # Log da criação do agente no agents.csv
        logger.log_agent(
            agent_id=self.aid.name,
            session_id=self.session_id,
            name=self.aid.name,
            state="Created"
        )
    
    def on_start(self):
        """Método chamado quando o agente inicia e registra no AMS."""
        super().on_start()
        display_message(self.aid.name, 'Agente pronto e registrado no AMS!')
        
        # Log do agente ativo
        logger.log_agent(
            agent_id=self.aid.name,
            session_id=self.session_id,
            name=self.aid.name,
            state="Active"
        )
        
        # Log do evento de inicialização no events.csv
        logger.log_event(
            event_type="agent_started",
            agent_id=self.aid.name,
            data={"port": self.aid.port}
        )

        # Envia para um agente vizinho em vez de autoenvio. Isso garante
        # tráfego real de rede e mantém o messages.csv sob responsabilidade do Sniffer.
        self.call_later(3.0, self.send_network_hello)

    def send_network_hello(self):
        """Envia uma mensagem FIPA-ACL para um agente vizinho."""
        mensagem = ACLMessage(ACLMessage.INFORM)
        mensagem.add_receiver(self.peer_aid)
        mensagem.set_ontology('hello_ontology')
        mensagem.set_content('Hello World Message! (Via Rede)')
        self.send(mensagem)
    
    def react(self, message):
        """Processa mensagens recebidas (para manter compatibilidade)."""
        super().react(message)
        
        # Formata o conteúdo para exibição segura
        formatted_content = format_message_content(message.content)
        
        # Se debug=True no __init__, ele vai printar a mensagem FIPA que acabou de receber dele mesmo
        if self.debug and message.content:
            display_message(self.aid.name, f'📨 Mensagem recebida: {formatted_content}')


if __name__ == '__main__':
    # Verifica se a porta base foi fornecida
    if len(argv) < 2:
        print("Uso: python agent_example_1_updated.py <porta_base>")
        print("Exemplo: python agent_example_1_updated.py 20000")
        exit(1)
    
    agents_per_process = 3
    c = 0
    agents = list()
    
    # Configuração do AMS
    ams_config = {'name': 'localhost', 'port': 8000}
    
    # Sessão única para todos os agentes
    session_id = get_shared_session_id()
    
    # Log da sessão no sessions.csv
    logger.log_session(
        session_id=session_id,
        name=f"HelloWorld_Session_{session_id}",
        state="Started"
    )
    
    aids = []
    for i in range(agents_per_process):
        port = int(argv[1]) + c
        agent_name = f'agent_hello_{port}@localhost:{port}'  # f-string (Python 3.6+)
        aids.append(AID(name=agent_name))
        c += 1000

    for index, aid in enumerate(aids):
        peer_aid = aids[(index + 1) % len(aids)]

        # Cria o agente
        agente_hello = AgenteHelloWorld(aid, peer_aid, session_id)

        # Configura o AMS para o agente
        agente_hello.update_ams(ams_config)

        agents.append(agente_hello)
        display_message('Sistema', f'Agente {aid.name} criado')
    
    display_message('Sistema', f'Iniciando {len(agents)} agentes...')
    
    # Log do início da execução no events.csv
    logger.log_event(
        event_type="test_started",
        data={
            "example": "agent_example_1",
            "num_agents": len(agents),
            "base_port": argv[1]
        }
    )
    
    start_loop(agents)
