'''
This file implements the needed Behaviour class extensions, in
order to PADE Scheduler be able to manage the agent behaviours.
'''

from pade.behaviours.protocols import Behaviour
from pade.acl.messages import ACLMessage
from time import sleep
import queue

class BaseBehaviour(Behaviour):

    ''' BaseBehaviour class ihnerits from Behaviour class and
    implements the basic methods for scheduled behaviours.
    '''

    def __init__(self, agent):
        ''' This method initializes a new instance of BaseBehaviour
        class and explicitly calls the Behaviour.__init__() method.
        '''
        super().__init__(agent)
        # Queue of received messages by the agent and unread by this behaviour
        self.messages = queue.Queue()
        # Lock object (to ensure the mutual exclusion, when needed)
        self.__lock = None


    def read(self, block = True):
        ''' It gets the first message in the local message queue.
        '''
        if block:
            return self.messages.get()
        else:
            try:
                return self.messages.get_nowait()
            except queue.Empty:
                return None


    def send(self, message):
        ''' This method gets a message and passes it to self.agent.send() method.
        It was coded just to complement the pair read/send in the BaseBehaviour class.
        The method self.agent.send() can still be used directly in the code.
        '''
        self.agent.send(message)


    def read_timeout(self, timeout):
        ''' It tries to read a message twice until the end of timeout.
        In cases of no messages, this method returns None
        '''
        message = self.read(block = False)
        if message != None:
            return message
        else:
            sleep(timeout)
            return self.read(block = False)


    def receive(self, message):
        ''' It sets a new message on local messages queue.
        '''
        if isinstance(message, ACLMessage):
            self.messages.put(message)
        else:
            raise ValueError('message object type must be ACLMessage!')



    def action(self):
        ''' This is an abstract method that must be overridden in the
        child classes, writing the main actions of this behaviour.
        '''
        pass


    def done(self):
        ''' This is an abstract method that must be overridden in the
        child classes, dealing with the finish of this behaviour.
        '''
        pass


    def wait(self, timeout):
        ''' This method sleeps a behaviour until occurs a timeout. The
        behaviour will execute normally afterwards.
        '''
        sleep(timeout)


    def on_end(self):
        ''' The scheduler will calls this method after the self.done()
        method returns True and before the end of this behaviour. It is
        the last action of a behaviour.
        '''
        pass


    def has_messages(self):
        ''' A method to returns if this behaviour has messages in its
        received messages queue.
        '''
        return self.messages.qsize() != 0


    def add_lock(self, lock):
        ''' Adds a threading.Lock object to this behaviour, allowing 
        it to execute the mutual exclusion correctly.
        '''
        self.__lock = lock
    

    def lock(self):
        ''' Tries to acquire the lock of the threading.Lock object.
        The behaviour will block if fails.
        '''
        self.__lock.acquire()
    

    def unlock(self):
        ''' Releases the lock of the threading.Lock object, allowing
        the other behaviours to acquire it.
        '''
        self.__lock.release()
