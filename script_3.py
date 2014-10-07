from protocols import FipaRequestProtocol
from agent import Agent
from utils import display_message, set_ams, start_loop
from messages import ACLMessage
from aid import AID

class RequestIniciante(FipaRequestProtocol):
	
	def __init__(self, agent, message):
		super(RequestIniciante, self).__init__(agent, message, is_initiator=True)
	
	def handle_agree(self, message):
		display_message(self.agent.aid.name, message.content)
	
	def handle_inform(self, message):
		display_message(self.agent.aid.name, message.content)

class RequestParticipante(FipaRequestProtocol):
	
	def __init__(self, agent):
		super(RequestParticipante, self).__init__(agent, message=None, is_initiator=False)
	
	def handle_request(self, message):
		display_message(self.agent.aid.name, message.content)
		
		response = message.create_reply()
		response.set_performative(ACLMessage.AGREE)
		response.set_content('AGREE')
		self.agent.send(response)
		
		response_2 = message.create_reply()
		response_2.set_performative(ACLMessage.INFORM)
		response_2.set_content('INFORM')
		self.agent.send(response_2)
		
class Agent_Initiator(Agent):
	def __init__(self, aid):
		Agent.__init__(self, aid)
		
		message = ACLMessage(ACLMessage.REQUEST)
		message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
		message.set_content('REQUEST')
		message.add_receiver('agent_participant_1')
		comportamento_1 = RequestIniciante(self, message)
		self.addBehaviour(comportamento_1)
	
	def on_start
on_start(self):
		Agent.on_start
on_start(self)

class Agent_Participant(Agent):
	def __init__(self, aid):
		Agent.__init__(self, aid)
		comportamento_1 = RequestParticipante(self)
		self.addBehaviour(comportamento_1)
		
	def on_start
on_start(self):
		Agent.on_start
on_start(self)

if __name__ == '__main__':
	
	set_ams(8000)
	
	agent_participant_1 = Agent_Participant(AID('agent_participant_1'))
	agent_participant_1.set_ams('localhost', 8000)
	agent_participant_1.start()
	
	agent_initiator = Agent_Initiator(AID('agent_initiator'))
	agent_initiator.set_ams('localhost', 8000)
	agent_initiator.start()
	
	start_loop()