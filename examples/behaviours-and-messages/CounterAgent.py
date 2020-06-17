''' This example shows how SimpleBehaviour works. The agent simply
counts from 0 to 30.
'''

from pade.behaviours.types import SimpleBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display, start_loop

class CounterAgent(Agent):
	def setup(self):
		# Passing an agent and a time to Count behaviour
		self.add_behaviour(Count(self, 30))


class Count(SimpleBehaviour):
	# Defining initial parameters to behaviour
	def __init__(self, agent, end):
		# This call to superclass is needed, passing the agent
		super().__init__(agent)
		# Defining counting variables
		self.counter = 0
		self.end = end

	def action(self):
		display(self.agent, 'Counting #%d' % self.counter)
		self.counter += 1

	# This method indicates when the behaviour finishes.
	def done(self):
		if self.counter > self.end:
			# The behaviour will stops when True is returned
			return True
		return False

	# This method is executed when the behaviour dies x_x
	def on_end(self):
		display(self.agent, 'Counting finished.')



if __name__ == '__main__':
	start_loop([CounterAgent('counter')])