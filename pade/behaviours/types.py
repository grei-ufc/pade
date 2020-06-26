'''
This file implements the BaseBehaviour class extensions. These classes
are used to model the agent behaviours.
'''

from pade.behaviours.base import BaseBehaviour
from pade.acl.messages import ACLMessage


class SimpleBehaviour(BaseBehaviour):
    ''' Class that implements the SimpleBehaviour.

    SimpleBehaviour class models a basic behaviour. The action() method must be
    overridden in the subclasses to define the behaviour actions. The done()
    method must indicate (by returning True) when this behaviour will finalize.

    Attributes
    ----------
    _return : object
        The data to be returned by this behaviour to another behaviour.
    _event : threading.Event()
        The event object used to implement the behaviour returning.
    '''

    def __init__(self, agent):
        ''' Simply calls the superclass __init__() method.
        '''
        super().__init__(agent)
        self._return = None
        self._event = threading.Event()


    def action(self):
        ''' This is an abstract method that must be overridden in the
        subclasses, implementing the main actions of this behaviour.
        '''
        pass


    def done(self):
        ''' This is an abstract method that must be overridden in the
        subclasses, dealing with the finish of this behaviour.
        '''
        pass

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


class OneShotBehaviour(BaseBehaviour):

    ''' OneShotBehaviour class models a finite behaviour. It executes its
    action() method only once.
    '''

    def __init__(self, agent):
        super().__init__(agent)

    def action(self):
        ''' This is an abstract method that must be overridden in the
        subclasses, implementing the main actions of this behaviour.
        '''
        pass

    def done(self):
        ''' This method ever returns True, indicating that the behaviour
        will execute only once. It should not be changed in subclasses.
        '''
        return True


class CyclicBehaviour(BaseBehaviour):

    ''' CyclicBehaviour class models an infinite behaviour. It executes its
    action() method until the end of the agent.
    '''

    def __init__(self, agent):
        super().__init__(agent)

    def action(self):
        ''' This is an abstract method that must be overridden in the
        subclasses, implementing the main actions of this behaviour.
        '''
        pass

    def done(self):
        ''' This method ever returns False, indicating that the behaviour
        will execute indefinitely. It should not be changed in subclasses.
        '''
        return False


class WakeUpBehaviour(OneShotBehaviour):

    ''' WakeUpBehaviour class models a finite behaviour. It executes its
    actions only once, after a timeout occurs. The actions of this class
    must be implemented into on_wake() method. A time value in seconds is 
    passed into its __init__() method. 
    '''

    def __init__(self, agent, time):
        super().__init__(agent)
        self.time = time

    def action(self):
        ''' This is a method that executes the general functions of this 
        behaviour type. It should not be changed in subclasses.
        '''
        self.wait(self.time)
        self.on_wake()

    def on_wake(self):
        ''' This is an abstract method that must be overridden in the
        subclasses, implementing the main actions of this behaviour.
        '''
        pass


class TickerBehaviour(CyclicBehaviour):

    ''' TickerBehaviour class models an infinite behaviour. It executes its
    actions after a timeout occurs, while the agent lives. The actions of 
    this class must be implemented into on_tick() method. A time value in
    seconds is passed into its __init__() method. 
    '''

    def __init__(self, agent, time):
        super().__init__(agent)
        self.time = time

    def action(self):
        ''' This is a method that executes the general functions of this 
        behaviour type. It should not be changed in subclasses.
        '''
        self.wait(self.time)
        self.on_tick()

    def on_tick(self):
        ''' This is an abstract method that must be overridden in the
        subclasses, implementing the main actions of this behaviour.
        '''
        pass


class SequentialBehaviour(OneShotBehaviour):

    ''' SequentialBehaviour class models a compound behaviour. It executes
    its sub-behaviours in a defined sequence. The execution order is defined
    at the time that the sub-behavious are added. No overrides are required
    in this class.
    '''

    def __init__(self, agent):
        super().__init__(agent)
        # Sub-behaviours list
        self.subbehaviours = list()

    def action(self):
        ''' This is a method that executes the general functions of this 
        behaviour type. It should not be changed in subclasses.
        '''
        for behaviour in self.subbehaviours:
            behaviour.action()
            while not behaviour.done():
                behaviour.action()
            behaviour.on_end()

    def add_subbehaviour(self, behaviour):
        ''' This method adds sub-behaviours in this behaviour
        '''
        self.subbehaviours.append(behaviour)

    def receive(self, message):
        ''' Overridden method to pass a received message to sub-behaviours.
        '''
        if isinstance(message, ACLMessage):
            for behaviour in self.subbehaviours:
                behaviour.messages.put(message)
        else:
            raise ValueError('message object type must be ACLMessage!')
