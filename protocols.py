# -*- encoding: utf-8 -*-
from messages import ACLMessage
from filters import Filter

class Behaviour(object):
	def __init__(self, agent):
		super(Behaviour, self).__init__()
		self.agent = agent
	
	def execute(self):
		pass
	
	def onStart(self):
		pass

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

