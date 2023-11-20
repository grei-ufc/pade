from twisted.internet import protocol
from pade.acl.messages import ACLMessage
from peer import PeerProtocol
import pickle

class Container(PeerProtocol):
    def __init__(self, container_id, port, fact):
        self.container_id = container_id
        self.port = port
        self.agents = {}  # Dicionário para armazenar agentes no container
        self.external_agents = {}  # Dicionário para armazenar agentes de outros contêineres
        self.fact = fact

    def get_container_ip(self):
        pass


    def add_agent(self, agent):
        self.agents[agent.agent_id] = agent

    def remove_agent(self, agent_id):
        if agent_id in self.agents:
            del self.agents[agent_id]

    def connectionMade(self):
        PeerProtocol.connectionMade(self)

    def connectionLost(self, reason):
        if self.message is not None:
            message = PeerProtocol.connectionLost(self, reason)
            self.message = None
            # executes the behaviour Agent.react to the received message.
            self.fact.react(message)

    def dataReceived(self, data):
        PeerProtocol.dataReceived(self, data)

        # Se a mensagem for recebida corretamente e for do tipo ACLMessage.INFORM
        if self.message is not None:
            try:
                received_message = pickle.loads(self.message)
                if received_message.performative == ACLMessage.INFORM:
                    sender_address = (received_message.sender.host, received_message.sender.port)
                    agent_id = received_message.sender.agent_id

                    # Verifica se o agente não está na lista self.agents e não está na lista self.external_agents
                    if agent_id not in self.agents and agent_id not in self.external_agents:
                        # Adiciona o endereço do agente externo à lista self.external_agents
                        self.external_agents[agent_id] = sender_address
            except Exception as e:
                print(f'Error processing received message: {e}')

            self.message = None

    def send_message(self, message, receiver_id=None):
        PeerProtocol.send_message(self, message)

    
    

    

    

    