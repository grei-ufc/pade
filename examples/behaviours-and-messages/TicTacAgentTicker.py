''' This example shows how TickerBehaviour works on PADE. An agent
prints a message in the screen every 1 second.
'''

from pade.behaviours.types import TickerBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop

class TicTacAgent(Agent):
	def setup(self):
		self.add_behaviour(NoiseBehaviour(self, 1))

class NoiseBehaviour(TickerBehaviour):
	def on_tick(self):
		display_message(self.agent, 'Tic-tac!')

if __name__ == '__main__':
	start_loop([TicTacAgent('tictac')])