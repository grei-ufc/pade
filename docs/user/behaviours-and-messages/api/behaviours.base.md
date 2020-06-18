<div role="main">

<div id="section-intro" class="section">

## Behaviours Module

This module implements the base of the Behaviours classes, in order to
enable the PADE Scheduler to manage the agent behaviours.


</div>


<div class="section">

## Classes

  - `  class BaseBehaviour (agent) `
    
    <div class="desc">
    
    The basic behaviour class.
    
    This class ihnerits from Behaviour class and implements the basic
    methods for scheduled behaviours.
    
    ##### Attributes
    
      - **`_messages`** : `list`  
        The behaviour local message queue.
      - **`_lock`** : `threding.Lock()`  
        The lock object used to implement mutual exclusion.
      - **`_return`** : `object`  
        The data to be returned by this behaviour to another behaviour.
      - **`_event`** : `threading.Event()`  
        The event object used to implement the behaviour returning.
    
    ##### Parameters
    
      - **`agent`** : `Agent`  
        The agent which performs the behaviour.
    
    </div>
    
    ##### Ancestors
    
      - pade.behaviours.protocols.Behaviour
    
    ##### Instance variables
    
      - `var lock`
        
        <div class="desc">
        
        Returns the added lock object.
        
        ##### Raises
        
          - `AttributeError`  
            If there is no a lock object added.
        
        ##### Returns
        
          - `threading.Lock`  
            The local lock object.
        
        </div>
    
    ##### Methods
    
      - `  def action(self) `
        
        <div class="desc">
        
        An abstract method that performs the actions of the behaviour.
        
        This method must be overridden in the subclasses.
        
        </div>
    
      - `  def add_lock(self, lock) `
        
        <div class="desc">
        
        Adds a threading.Lock object to this behaviour.
        
        This allows the behaviour to execute the mutual exclusion.
        
        ##### Parameters
        
          - **`lock`** : `threadong.Lock`  
            The lock object.
        
        </div>
    
      - `  def done(self) `
        
        <div class="desc">
        
        Defines when the behaviour ends.
        
        This method must be overridden in the subclasses.
        
        </div>
    
      - `  def has_messages(self) `
        
        <div class="desc">
        
        Checks whether the behaviour has messages in its messages queue.
        
        ##### Returns
        
          - `bool`  
            True if the queue has messages; False otherwise.
        
        </div>
    
      - `  def on_end(self) `
        
        <div class="desc">
        
        Executes the final actions of the behaviou.
        
        The scheduler will call this method after the behaviour ends.
        May be overriden in subclasses.
        
        </div>
    
      - `  def read(self, block=True) `
        
        <div class="desc">
        
        Reads a message from the local queue.
        
        It gets the first message in the local message queue. It waits
        (by default) to receive a message, in case of the queue is
        empty.
        
        ##### Parameters
        
          - **`block`** : `bool`, optional  
            Defines wheter the behaviour will block (block = True) or
            not (block = False) when the local message queue is empty
            (default is True).
        
        ##### Returns
        
          - `ACLMessage`  
            The read message from the local queue.
        
        </div>
    
      - `  def read_timeout(self, timeout) `
        
        <div class="desc">
        
        Reads the local queue waiting for a defined timeout.
        
        It tries to read the message queue twice until the end of
        timeout. In case of no messages, this method returns None.
        
        ##### Parameters
        
          - **`timeout`** : `float`  
            The max timeout to wait when reading the local message
            queue.
        
        ##### Returns
        
          - `ACLMessage`  
            The read message from the local queue.
          - `None`  
            In case of no messages in queue at the end of the timeout.
        
        </div>
    
      - `  def receive(self, message) `
        
        <div class="desc">
        
        Sets a new message in the local messages queue.
        
        ##### Parameters
        
          - **`message`** : `ACLMessage`  
            The message to be put in the queue.
        
        ##### Raises
        
          - `ValueError`  
            If the passed object not is an ACLMessage object.
        
        </div>
    
      - `  def send(self, message) `
        
        <div class="desc">
        
        Sends a message for other agents.
        
        This method gets a message and passes it to self.agent.send()
        method. It was coded just to complement the pair read/send in
        the BaseBehaviour class. The method self.agent.send() can still
        be used directly in the code.
        
        ##### Parameters
        
          - **`message`** : `ACLMessage`  
            The message to be sent.
        
        </div>
    
      - `  def set_return(self, data) `
        
        <div class="desc">
        
        Sets the return for this behaviour.
        
        ##### Parameters
        
          - **`data`** : `object`  
            The data to be returned by the behaviour.
        
        </div>
    
      - `  def wait(self, timeout) `
        
        <div class="desc">
        
        Sleeps a behaviour until occurs a timeout.
        
        ##### Parameters
        
          - **`timeout`** : `float`  
            The time to be waited.
        
        </div>
    
      - `  def wait_return(self, behaviour, timeout=None) `
        
        <div class="desc">
        
        Waits for the return from other behaviour.
        
        Whether the target behaviour return is not set, this method will
        block the behaviour until the return is set.
        
        ##### Parameters
        
          - **`behaviour`** : `BaseBehaviour`  
            The behaviour you want to get the return.
          - **`timeout`** : `float`, optional  
            The max timeout to wait the target behaviour returns.
        
        ##### Returns
        
          - `object`  
            The return data.
        
        </div>

</div>

# Index

<div class="toc">

  - [Behaviours module](#behaviours-module)

</div>

  - ### Super-module
    
      - `behaviours`

  - ### [Classes](#classes)
    
      - #### `BaseBehaviour`
        
          - `action`
          - `add_lock`
          - `done`
          - `has_messages`
          - `lock`
          - `on_end`
          - `read`
          - `read_timeout`
          - `receive`
          - `send`
          - `set_return`
          - `wait`
          - `wait_return`

</div>

Generated by [pdoc 0.8.1](https://pdoc3.github.io/pdoc).
