from pade.behaviours.types import OneShotBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display, start_loop
import threading


class Sequential(Agent):
	def setup(self):
		# Creating a Lock object
		lock = threading.Lock()
		# Creating the behaviours
		count1 = Count1_10(self)
		count2 = Count11_20(self)
		count3 = Count21_30(self)
		# Adding the same lock to behaviours we
		# want the mutual exclusion
		count1.add_lock(lock)
		count2.add_lock(lock)
		count3.add_lock(lock)
		# Adding the behaviours on agent
		self.add_behaviour(count1)
		self.add_behaviour(count2)
		self.add_behaviour(count3)

# Behaviour that counts from 1 to 10
class Count1_10(OneShotBehaviour):
	def action(self):
		self.lock() # Here starts the critical section (holds the lock)
		display(self.agent, 'Now, I will count from 1 to 10 slowly:')
		for num in range(1,11):
			display(self.agent, num)
			self.wait(1) # I put this so that we can see the behaviours blocking
		self.unlock() # Here ends the critical section (releases the lock)

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