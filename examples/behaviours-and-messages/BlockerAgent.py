from pade.behaviours.types import CyclicBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop


class BlockerAgent(Agent):
	def setup(self):
		self.add_behaviour(BlockBehaviour(self))


class BlockBehaviour(CyclicBehaviour):
	def action(self):
		message = self.read()
		display_message(self.agent, 'Running my behaviour...')


if __name__ == '__main__':
	start_loop([BlockerAgent('blocker', ignore_ams = False)])
