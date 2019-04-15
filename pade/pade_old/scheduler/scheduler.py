'''
This file implements the basic functionalities of the PADE
Scheduler. The Scheduler aims to manage the agent behaviours,
so that PADE provides new methods to control the behaviours
of the system agents.
'''

from threading import Thread

''' Scheduler class: basically, executes the behaviours (under
'task form') in the active tasks queue.
'''
class Scheduler(object):
	def __init__(self, agent):
		self.agent = agent
		self.active_tasks = list() # Active tasks queue
		self.blocked_tasks = list() # Blocked tasks queue
		self.running = False # Indicate if the scheduler is running

	def run(self):
		self.running = True
		while len(self.active_tasks) > 0:
			task = self.active_tasks[0]
			task.start()
			self.dequeue()
		self.running = False

	def enqueue(self, task):
		if isinstance(task, Task):
			self.active_tasks.append(task)
			self.wakeup()
		else:
			raise ValueError('task object type must be Task!')

	def dequeue(self):
		self.active_tasks = self.active_tasks[1:]

	def wakeup(self):
		if not self.running:
			self.run()

	def unblock_behaviours(self):
		self.active_tasks += self.blocked_tasks
		self.blocked_tasks.clear()
		self.wakeup()

	def block(self, task):
		if isinstance(task, Task):
			self.blocked_tasks.append(task)
		else:
			raise ValueError('task object type must be Task!')

	def add_behaviour(self, behaviour):
		if isinstance(behaviour, Behaviour):
			self.enqueue(Task(behaviour, self))
		else:
			raise ValueError('behaviour object type must be Behaviour!')


''' Task class: manages a behaviour separately in a thread, 
deciding whether a behaviour must goes to active queue or to blocked
queue.
'''
class Task(Thread):
	def __init__(self, behaviour, scheduler):
		self.behaviour = behaviour
		self.scheduler = scheduler

	def run(self):
		self.behaviour.action() # Execute the behaviour actions
		if not self.behaviour.done(): # Verifies if the behaviour will execute again
			scheduler.enqueue(self)
		else:
			del self.behaviour