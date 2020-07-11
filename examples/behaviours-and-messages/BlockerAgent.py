''' This example shows how the agents can ignore the AMS messages
or not: that is programmer's choice (using the parameter
ignore_ams). This behaviour will unblock every times the agent
receives a message from AMS.
'''

from pade.behaviours.types import CyclicBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop


class BlockerAgent(Agent):
	def setup(self):
		self.add_behaviour(BlockBehaviour(self))


class BlockBehaviour(CyclicBehaviour):
	def action(self):
		message = self.agent.receive()
		if message != None:
			display_message(self.agent, 'Running my behaviour...')
		else:
			self.block()


if __name__ == '__main__':
	start_loop([BlockerAgent('blocker', ignore_ams = False)])
