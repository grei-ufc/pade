'''
This file implements the basic functionalities of the PADE
Scheduler. The Scheduler aims to manage the agent behaviours,
so that PADE provides new methods to control the behaviours
of the system agents.
'''

from threading import Thread
from pade.behaviours.base import BaseBehaviour
from pade.misc.utility import display
from queue import Queue

class Scheduler(Thread):
    ''' Scheduler class basically executes each behaviour within a
    thread (under BehaviourTask form, here called simply 'Task').
    '''

    def __init__(self, agent):
        super().__init__()
        self.agent = agent
        self.active_tasks = list() # Active tasks queue
        self.tasks = Queue() # Tasks queue

    def run(self):
        ''' It executes all scheduled tasks in the 'tasks' queue.
        '''
        while self.agent.active:
            task = self.tasks.get()
            task.start()


class BehaviourTask(Thread):
    ''' The Task class manages each behaviour separately in an one thread,
    deciding whether a behaviour must goes to active queue or to blocked
    queue. Each instance of this class runs a behaviour once only.
    '''
    def __init__(self, behaviour, scheduler):
        super().__init__()
        self.behaviour = behaviour
        self.scheduler = scheduler

    def run(self):
        ''' This method executes the BaseBehaviour.action() method, until
        it returns False (i.e, until its end).
        '''
        self.behaviour.action() # Execute the action() method at least once.
        while not self.behaviour.done():
            self.behaviour.action() # Execute the behaviour actions
        self.behaviour.on_end() # Lasts actions of the behaviour
        self.scheduler.agent.remove_task(self) # Thread will die after its behaviour execution 
