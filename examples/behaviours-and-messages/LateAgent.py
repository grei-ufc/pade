# Needed imports
from pade.behaviours.types import WakeUpBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop

# Defining the LaterAgent (inherits from Agent class)
class LateAgent(Agent):

	# This method will execute at agent startup
	def setup(self):
		# The behaviour is created with two args, where
		# the second is a time (in seconds) to behaviour
		# waits.
		behaviour = AmILate(self, 5)
		# It adds a behaviour in the agent
		self.add_behaviour(behaviour)


# Defining the AmILate behaviour
class AmILate(WakeUpBehaviour):

	# This method executes the main actions of behaviour
	def on_wake(self):
		display_message(self.agent, 'Am I late?')


# It starts the agents with PADE
if __name__ == '__main__':
	# Defining a LateAgent object
	lateagent = LateAgent('late')
	# Creating a list with agents that will be executed
	agents_list = [lateagent]
	# Passing the agent list to main loop of PADE
	start_loop(agents_list)