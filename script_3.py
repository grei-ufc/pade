from protocols import FIPA_Request_Protocol
from agent import Agent
from utils import displayMessage, startAMS, startLoop
from messages import ACLMessage
from aid import AID

class RequestIniciante(FIPA_Request_Protocol):
	
	def __init__(self, agent, message):
		super(RequestIniciante, self).__init__(agent, message, isInitiator=True)
	
	def handleAgree(self, message):
		displayMessage(self.agent.aid.name, message.content)
	
	def handleInform(self, message):
		displayMessage(self.agent.aid.name, message.content)

class RequestParticipante(FIPA_Request_Protocol):
	
	def __init__(self, agent):
		super(RequestParticipante, self).__init__(agent, message=None, isInitiator=False)
	
	def handleRequest(self, message):
		displayMessage(self.agent.aid.name, message.content)
		
		response = message.createReply()
		response.setPerformative(ACLMessage.AGREE)
		response.setContent('AGREE')
		self.agent.send(response)
		
class Agent_Initiator(Agent):
	def __init__(self, aid):
		Agent.__init__(self, aid)
		
		message = ACLMessage(ACLMessage.REQUEST)
		message.setProtocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
		message.setContent('REQUEST')
		message.addReceiver('agent_participant')
		comportamento_1 = RequestIniciante(self, message)
		self.addBehaviour(comportamento_1)
	
	def onStart(self):
		Agent.onStart(self)

class Agent_Participant(Agent):
	def __init__(self, aid):
		Agent.__init__(self, aid)
		comportamento_1 = RequestParticipante(self)
		self.addBehaviour(comportamento_1)
		
	def onStart(self):
		Agent.onStart(self)

if __name__ == '__main__':
	
	startAMS(8000)
	
	agent_participant = Agent_Participant(AID('agent_participant'))
	agent_participant.setAMS('localhost', 8000)
	agent_participant.start()
	
	agent_initiator = Agent_Initiator(AID('agent_initiator'))
	agent_initiator.setAMS('localhost', 8000)
	agent_initiator.start()
	
	startLoop()