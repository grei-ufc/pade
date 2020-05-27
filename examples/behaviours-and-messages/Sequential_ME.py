from pade.behaviours.types import OneShotBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display, start_loop
import threading


class Sequential(Agent):
	def setup(self):
		# Creating a Lock object to the behaviours which
		# we want the mutual exclusion
		lock = threading.Lock()
		# Adding the behaviours and passing to them the
		# same created lock object
		self.add_behaviour(Count1_10(self, lock = lock))
		self.add_behaviour(Count11_20(self, lock = lock))
		self.add_behaviour(Count21_30(self, lock = lock))

# Behaviour that counts from 1 to 10
class Count1_10(OneShotBehaviour):
	def action(self):
		self.lock() # Here starts the critical section
		display(self.agent, 'Now, I will count from 1 to 10 slowly:')
		for num in range(1,11):
			display(self.agent, num)
			self.wait(1) # I put this so that we can see the behaviours blocking
		self.unlock() # Here ends the critical section

# Behaviour that counts from 11 to 20
class Count11_20(OneShotBehaviour):
	def action(self):
		self.lock()
		display(self.agent, 'Now, I will count from 11 to 20 slowly:')
		for num in range(11,21):
			display(self.agent, num)
			self.wait(1)
		self.unlock()

# Behaviour that counts from 21 to 30
class Count21_30(OneShotBehaviour):
	def action(self):
		self.lock()
		display(self.agent, 'Now, I will count from 21 to 30 slowly:')
		for num in range(21,31):
			display(self.agent, num)
			self.wait(1)
		self.unlock()


if __name__ == '__main__':
	start_loop([Sequential('seq')])