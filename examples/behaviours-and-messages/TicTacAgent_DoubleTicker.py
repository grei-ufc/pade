from pade.behaviours.types import TickerBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop

'''
This example presents two different TickerBehaviour
running in paralell and in an alternating way
'''

class TicTacAgent(Agent):
	def setup(self):
		self.add_behaviour(TicBehaviour(self, 1))
		self.add_behaviour(TacBehaviour(self, 1))

class TicBehaviour(TickerBehaviour):
	def on_tick(self):
		display_message(self.agent, 'Tic')

class TacBehaviour(TickerBehaviour):
	def on_tick(self):
		display_message(self.agent, 'Tac')

if __name__ == '__main__':
	start_loop([TicTacAgent('tictac')])
