# -*- encoding: utf-8 -*-
from messages import ACLMessage
from filters import Filter
from time import time

class Behaviour(object):
	def __init__(self, agent):
		super(Behaviour, self).__init__()
		self.agent = agent
		self.t1 = 0
		self.t2 = 0
		self.timeout = 1
		self.timesleep = 0.5
		
	def execute(self):
		pass
	
	def timedBehaviour(self):
		pass
	
	def onStart(self):
		self.t1 = int(time())

class FIPA_Request_Protocol(Behaviour):
	
	def __init__(self, agent, message=None, isInitiator=True):
		super(FIPA_Request_Protocol, self).__init__(agent)
		
		self.isInitiator = isInitiator
		self.message = message
		
		self.filter_protocol = Filter()
		self.filter_protocol.setProtocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
		
		self.filter_Request = Filter()
		self.filter_Request.setPerformative(ACLMessage.REQUEST)
		
		self.filter_Refuse = Filter()
		self.filter_Refuse.setPerformative(ACLMessage.REFUSE)
		
		self.filter_Agree = Filter()
		self.filter_Agree.setPerformative(ACLMessage.AGREE)
		
		self.filter_Failure = Filter()
		self.filter_Failure.setPerformative(ACLMessage.FAILURE)
		
		self.filter_Inform = Filter()
		self.filter_Inform.setPerformative(ACLMessage.INFORM)
	
	def onStart(self):
		
		Behaviour.onStart(self)
		
		if self.isInitiator and self.message != None:
			self.agent.send(self.message)
	
	def handleRequest(self, message):
		pass
	
	def handleRefuse(self, message):
		pass
	
	def handleAgree(self, message):
		pass
	
	def handleFailure(self, message):
		pass
	
	def handleInform(self, message):
		pass
	
	def execute(self, message):
		
		self.message = message
		
		if self.filter_protocol.filter(self.message):
			
			if self.filter_Request.filter(self.message):
				self.handleRequest(message)
				
			elif self.filter_Refuse.filter(self.message):
				self.handleRefuse(message)
				
			elif self.filter_Agree.filter(self.message):
				self.handleAgree(message)
				
			elif self.filter_Failure.filter(self.message):
				self.handleFailure(message)
				
			elif self.filter_Inform.filter(self.message):
				self.handleInform(message)
				
			else:
				return
		else:
			return

class FIPA_ContractNet_Protocol(Behaviour):
	
	def __init__(self, agent, message=None, isInitiator=True):
		super(FIPA_ContractNet_Protocol, self).__init__(agent)
		
		self.isInitiator = isInitiator
		self.CFP_Qtd = 0
		self.received_Qtd = 0
		
		self.proposes = []
		
		self.message = message
		
		self.filter_protocol = Filter()
		self.filter_protocol.setProtocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)
		
		self.filter_CFP = Filter()
		self.filter_CFP.setPerformative(ACLMessage.CFP)
		
		self.filter_Refuse = Filter()
		self.filter_Refuse.setPerformative(ACLMessage.REFUSE)
		
		self.filter_Propose = Filter()
		self.filter_Propose.setPerformative(ACLMessage.PROPOSE)
		
		self.filter_Accept_Propose = Filter()
		self.filter_Accept_Propose.setPerformative(ACLMessage.ACCEPT_PROPOSAL)
		
		self.filter_Reject_Propose = Filter()
		self.filter_Reject_Propose.setPerformative(ACLMessage.REJECT_PROPOSAL)
		
		self.filter_Failure = Filter()
		self.filter_Failure.setPerformative(ACLMessage.FAILURE)
		
		self.filter_Inform = Filter()
		self.filter_Inform.setPerformative(ACLMessage.INFORM)
	
	def onStart(self):
		Behaviour.onStart(self)
		
		if self.isInitiator and self.message != None:
			
			if self.message.performative == ACLMessage.CFP:
				
				self.CFP_Qtd = len(self.message.receivers)
				
				self.agent.send(self.message)
	
	def handleCFP(self, message):
		pass
	
	def handlePropose(self, message):
		self.received_Qtd += 1
	
	def handleRefuse(self, message):
		self.received_Qtd += 1
	
	def handleAllProposes(self, proposes):
		pass
	
	def handleInform(self, message):
		pass
	
	def handleRejectPropose(self, message):
		pass
	
	def handleAcceptPropose(self, message):
		pass
	
	def timedBehaviour(self):
		Behaviour.timedBehaviour(self)
		
		from time import sleep
		self.t2 = int(time())
		while True:
			sleep(self.timesleep)
			if self.t2 - self.t1 > self.timeout:
				self.handleAllProposes(self.proposes)
				self.t1 = 0
				self.t2 = 0
		
	def execute(self, message):
		
		Behaviour.execute(self)
		
		self.message = message
			
		if self.filter_protocol.filter(self.message):
			if self.filter_CFP.filter(self.message):
				self.handleCFP(message)
				
			elif self.filter_Propose.filter(self.message):
				self.proposes.append(message)
				self.handlePropose(message)
				
				if self.received_Qtd == self.CFP_Qtd:
					self.handleAllProposes(self.proposes)
				
			elif self.filter_Refuse.filter(self.message):
				self.proposes.append(message)
				self.handleRefuse(message)
				
				if self.received_Qtd == self.CFP_Qtd:
					self.handleAllProposes(self.proposes) 
				
			elif self.filter_Accept_Propose.filter(self.message):
				self.handleAcceptPropose(message)
				
			elif self.filter_Reject_Propose.filter(self.message):
				self.handleRejectPropose(message)
				
			elif self.filter_Failure.filter(self.message):
				self.handleFailure(message)
				
			elif self.filter_Inform.filter(self.message):
				self.handleInform(message)
				
			else:
				return
			
		else:
			return
