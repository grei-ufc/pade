from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.misc.data_logger import logger
from sys import argv
from datetime import datetime

class AgenteHelloWorld(Agent):
    def __init__(self, aid):
        super().__init__(aid=aid)
        
    def on_start(self):
        super().on_start()
        display_message(self.aid.localname, 'Hello World!')
        
        # Send a message to itself to trigger the PADE Sniffer and populate messages.csv
        mensagem = ACLMessage(ACLMessage.INFORM)
        mensagem.set_sender(self.aid)
        mensagem.add_receiver(self.aid)
        mensagem.set_content('Hello World Message!')
        self.send(mensagem)

if __name__ == '__main__':
    # Define the AMS configuration
    ams_config = {'name': 'localhost', 'port': 8000}
    
    # Initialize the session logger (CSV)
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.log_session(session_id=session_id, name="HelloWorld_Test", state="Started")

    # Start 1 agent
    agents_per_process = 1
    c = 0
    agents = list()
    
    # Define the base port via argument or use a default
    base_port = int(argv[1]) if len(argv) > 1 else 20000
    
    for i in range(agents_per_process):
        port = base_port + c
        agent_name = f'agente_hello_{port}@localhost:{port}'
        
        agente_hello = AgenteHelloWorld(AID(name=agent_name))
        agente_hello.update_ams(ams_config)
        agents.append(agente_hello)
        c += 1000
    
    start_loop(agents)