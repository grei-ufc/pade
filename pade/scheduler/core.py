"""Framework for Intelligent Agents Development - PADE

The MIT License (MIT)

Copyright (c) 2019 Lucas S Melo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Scheduler module
----------------

This module implements the basic functionalities of the PADE Scheduler. The
scheduler aims to manage the agent behaviours, so that PADE can provide the
support for finite, infinite and compound behaviours.

@author: Italo Campos
"""

from threading import Thread
from pade.behaviours.base import BaseBehaviour
from pade.misc.utility import display
from queue import Queue

class Scheduler(Thread):
    ''' This class models behaviours scheduler of PADE.

    Scheduler class basically envelopes each behaviour within a thread (under
    BehaviourTask form, here called simply 'Task') and execute it.

    Attributes
    ----------
    agent : Agent
        The agent that executes the behaviour.
    active_tasks : list
        The queue of the active behaviours (in the task form).
    tasks : queue
        The entire queue of tasks in the scheduler.
    '''

    def __init__(self, agent):
        '''
        Parameters
        ----------
        agent : Agent
            The agent that executes the behaviour.
        '''

        super().__init__()
        self.agent = agent
        self.active_tasks = list()
        self.tasks = Queue()


    def run(self):
        ''' Executes the scheduled tasks in the 'tasks' queue.
        '''

        while self.agent.active:
            task = self.tasks.get()
            task.start()


class BehaviourTask(Thread):
    ''' This class encapsulates each behaviour in a thread.

    A Task is a separated thread that deals with the execution of each
    important method of the behaviours.

    Attributes
    ----------
    behaviour : BaseBehaviour
        The behaviour encapsulated in the task.
    scheduler : Scheduler
        A reference to the scheduler in which this task is executed.
    '''

    def __init__(self, behaviour, scheduler):
        '''
        Parameters
        ----------
        behaviour : BaseBehaviour
            The behaviour encapsulated in the task.
        scheduler : Scheduler
            A reference to the scheduler in which this task is executed.
        '''

        super().__init__()
        self.behaviour = behaviour
        self.scheduler = scheduler


    def run(self):
        ''' Runs the behaviour.

        This method will run the action methods (action() and on_end()) of the
        BaseBehaviour class, controlled by the done() method.
        '''

        self.behaviour.action() # Execute the action() method at least once.
        while not self.behaviour.done():
            self.behaviour.action() # Execute the behaviour actions
        self.behaviour.on_end() # Lasts actions of the behaviour
        self.scheduler.agent.remove_task(self) # Thread will die after its behaviour execution 
