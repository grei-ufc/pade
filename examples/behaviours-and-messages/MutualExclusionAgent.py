from pade.behaviours.types import CyclicBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display, start_loop
import threading


class MutualExclusionAgent(Agent):
	def setup(self):
		# Creating a Lock object
		lock = threading.Lock()
		# Creating the behaviours
		say_biscoito = SayBiscoito(self)
		say_bolacha = SayBolacha(self)
		# Passing the same lock object to behaviours
		say_bolacha.add_lock(lock)
		say_biscoito.add_lock(lock)
		# Adding the behaviours in the agent
		self.add_behaviour(say_biscoito)
		self.add_behaviour(say_bolacha)

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