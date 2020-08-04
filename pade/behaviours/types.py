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

Behaviour types module
----------------------

This module implements the BaseBehaviour class extensions. These subclasses are
used to model the agent behaviours of various types.

@author: Italo Campos
"""

from pade.behaviours.base import BaseBehaviour
from pade.acl.messages import ACLMessage
import queue, threading


class SimpleBehaviour(BaseBehaviour):
    ''' Class that implements the SimpleBehaviour.

    SimpleBehaviour class models a basic behaviour. The action() method must be
    overridden in the subclasses to define the behaviour actions. The done()
    method must indicate (by returning True) when this behaviour will finalize.

    Attributes
    ----------
    _lock : threding.Lock()
        The lock object used to implement mutual exclusion.
    _return : object
        The data to be returned by this behaviour to another behaviour.
    _event : threading.Event()
        The event object used to implement the behaviour returning.
    '''

    def __init__(self, agent):
        '''
        Parameters
        ----------
        agent : Agent
            The agent which performs the behaviour.
        '''

        super().__init__(agent)
        self._lock = None
        self._return = None
        self._event = threading.Event()


    def action(self):
        '''  An abstract method that performs the actions of the behaviour.

        This method can be overridden in the subclasses.
        '''

        pass


    def done(self):
        ''' Defines when the behaviour ends.

        This method must be overridden in the subclasses, defining exactly when
        the behaviour will ends (by returning True).
        '''

        pass


    def add_lock(self, lock):
        ''' Adds a threading.Lock object to this behaviour.

        This allows the behaviour to execute the mutual exclusion.

        Parameters
        ----------
        lock : threadong.Lock
            The lock object.
        '''

        self._lock = lock


    @property
    def lock(self):
        ''' Returns the added lock object.

        Raises
        ------
        AttributeError
            If there is no a lock object added.

        Returns
        -------
        threading.Lock
            The local lock object.
        '''

        if self._lock != None:
            return self._lock
        else:
            raise(AttributeError('No such lock object added to this behaviour.'))


    def set_return(self, data):
        ''' Sets the return for this behaviour.

        Parameters
        ----------
        data : object
            The data to be returned by the behaviour.
        '''

        self._return = data
        self._event.set()


    def wait_return(self, behaviour, timeout = None):
        ''' Waits for the return from other behaviour.

        Whether the target behaviour return is not set, this method
        will block the behaviour until the return is set.

        Parameters
        ----------
        behaviour : BaseBehaviour
            The behaviour you want to get the return.
        timeout : float, optional
            The max timeout to wait the target behaviour returns.

        Returns
        -------
        object
            The return data.
        '''

        behaviour._event.wait(timeout)
        behaviour._event.clear()
        return behaviour._return



class CompoundBehaviour(BaseBehaviour):
    ''' This class models compound behaviours in PADE.

    CompoundBehaviour is an abstract class to model behaviours that handle
    other behaviours as sub-behaviours. This classe implements the general
    add_subbehaviour(SimpleBehaviour) method that add simple behaviours in the
    local queue as sub-behaviours. The actions of this class need to be
    implemented in subclasses.

    Attributes
    ----------
    _subbehaviours : list
        The list of added subbehaviours.
    '''

    def __init__(self, agent):
        '''
        Parameters
        ----------
        agent : Agent
            The agent that holds the behaviour.
        '''

        super().__init__(agent)
        self.subbehaviours = list()


    def add_subbehaviour(self, behaviour):
        ''' Adds sub-behaviours in this sub-behaviour local list.

        Parameters
        ----------
        behaviour : SimpleBehaviour
            The simple behaviour to be added as sub-behaviour.

        Raises
        ------
        ValueError
            If the sub-behaviour not it a subclass from SimpleBehaviour.
        '''

        if isinstance(behaviour, SimpleBehaviour):
            self.subbehaviours.append(behaviour)
        else:
            raise ValueError('sub-behaviours must be of the type SimpleBehaviour!')


    def receive(self, message):
        ''' Passes the received message to the sub-behaviours.

        This method doesn't save the messages in the local queue, by default.
        If you want to change that behaviour, override this method in the
        subclasses.

        Parameters
        ----------
        message : ACLMessage
            The message to be passed to the sub-behaviours.

        Raises
        ------
        ValueError
            If the passed object is not an ACLMessage.
        '''

        if isinstance(message, ACLMessage):
            for behaviour in self.subbehaviours:
                behaviour.receive(message)
        else:
            raise ValueError('message object type must be ACLMessage!')



class OneShotBehaviour(SimpleBehaviour):
    ''' This class models a finite behaviour.

    OneShotBehaviour are behaviours that executes its action() method only 
    once.
    '''

    def action(self):
        '''  An abstract method that performs the actions of the behaviour.

        This method can be overridden in the subclasses.
        '''

        pass


    def done(self):
        ''' Defines when the behaviour ends.

        This method always returns True and should not be overridden in the
        subclasses. By returning True, the behaviour will execute only once.
        '''

        return True



class CyclicBehaviour(SimpleBehaviour):
    ''' This class models an infinite behaviour.

    CyclicBehaviour are behaviours that executes its action() method until the
    end of the agent.
    '''

    def action(self):
        '''  An abstract method that performs the actions of the behaviour.

        This method can be overridden in the subclasses.
        '''

        pass


    def done(self):
        ''' Defines when the behaviour ends.

        This method always returns False and should not be overridden in the
        subclasses. By returning False, the behaviour will execute
        indefinitely.
        '''

        return False



class WakeUpBehaviour(OneShotBehaviour):
    ''' This class models a finite behaviour that waits a timeout before
    performs its actions.

    WakeUpBehaviour class models a finite behaviour that executes its actions
    after a timeout. The actions of this class must be implemented into the
    on_wake() method.

    Attributes
    ----------
    time : float
        The amount of time (in seconds) to be waited before the behaviour
        performs its actions.
    '''

    def __init__(self, agent, time):
        '''
        Parameters
        ----------
        agent : Agent
            The agent that executes the behaviour.
        time : float
            The amount of time (in seconds) to be waited before the behaviour
            performs its actions.
        '''

        super().__init__(agent)
        self.time = time


    def action(self):
        ''' This method performs the actions of the behaviour.

        This method should not be overridden in the subclasses. Use the method
        on_wake() to write the actions of this behaviour.
        '''

        self.wait(self.time)
        self.on_wake()


    def on_wake(self):
        '''  An abstract method that performs the actions of the behaviour.

        This method can be overridden in the subclasses.
        '''

        pass



class TickerBehaviour(CyclicBehaviour):
    ''' This class models an infinite behaviour that waits a timeout before
    performs its actions.

    TickerBehaviour class models an infinite behaviour that always waits a
    timeout before execute its actions. The actions of this class must be
    implemented into the on_tick() method.

    Attributes
    ----------
    time : float
        The amount of time (in seconds) to be waited before each execution of
        the behaviour.
    '''

    def __init__(self, agent, time):
        '''
        Parameters
        ----------
        agent : Agent
            The agent that executes the behaviour.
        time : float
            The amount of time (in seconds) to be waited before each execution
            of the behaviour.
        '''

        super().__init__(agent)
        self.time = time


    def action(self):
        ''' This method performs the actions of the behaviour.

        This method should not be overridden in the subclasses. Use the method
        on_tick() to write the actions of this behaviour.
        '''

        self.wait(self.time)
        self.on_tick()


    def on_tick(self):
        '''  An abstract method that performs the actions of the behaviour.

        This method can be overridden in the subclasses.
        '''

        pass



class SequentialBehaviour(CompoundBehaviour):
    ''' This class models the sequential-compound behaviours in PADE.

    SequentialBehaviour models a sequential-compound behaviour. This classe
    adds SimpleBehaviour and its subclasses as sub-behaviours, and execute them
    sequentially. The execution order is defined as the sub-behavious are
    added. No overrides are required for this class.
    '''

    def action(self):
        ''' This method performs the actions of the behaviour.

        This method executes sequentially the sub-behaviours. This method
        should not be overridden in the subclasses.
        '''

        for behaviour in self.subbehaviours:
            behaviour.action()
            while not behaviour.done():
                behaviour.action()
            behaviour.on_end()


    def done(self):
        ''' Defines when the behaviour ends.

        This method always returns True and should not be overridden in the
        subclasses. By returning True, the behaviour will execute only once.
        '''

        return True
