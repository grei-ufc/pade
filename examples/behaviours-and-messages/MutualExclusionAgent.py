from pade.behaviours.types import CyclicBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display, start_loop
import threading


class MutualExclusionAgent(Agent):
	def setup(self):
		# Creating a Lock object
		lock = threading.Lock()
		# Adding the behaviours and passing the same lock
		# object to them
		self.add_behaviour(SayBiscoito(self, lock = lock))
		self.add_behaviour(SayBolacha(self, lock = lock))

class SayBiscoito(CyclicBehaviour):
	def action(self):
		self.lock() # Starts the critical section
		for _ in range(5): # The agent will hold the lock by 5 prints
			display(self.agent, 'The correct name is "BISCOITO".')
			self.wait(0.5)
		self.unlock() # Ends the critical section

class SayBolacha(CyclicBehaviour):
	def action(self):
		self.lock()
		# Here the agent will hold the lock only by 1 print, and 
		# release it right away
		display(self.agent, '"BOLACHA" is the correct name.')
		self.unlock()


if __name__ == '__main__':
	start_loop([MutualExclusionAgent('mea')])