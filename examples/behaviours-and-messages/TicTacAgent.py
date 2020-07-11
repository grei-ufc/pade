''' This example shows how CyclicBehaviour works on PADE. Also, this
example shows how the wait() method works. An agent prints a message
in the screen every 1 second.
'''

from pade.behaviours.types import CyclicBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop

class TicTacAgent(Agent):
	def setup(self):
		self.add_behaviour(NoiseBehaviour(self))


class NoiseBehaviour(CyclicBehaviour):
	def action(self):
		display_message(self.agent, 'Tic-tac!')
		self.wait(1) # The behaviour will sleep by 1 second


if __name__ == '__main__':
	tic = TicTacAgent('tictac')
	start_loop([tic])