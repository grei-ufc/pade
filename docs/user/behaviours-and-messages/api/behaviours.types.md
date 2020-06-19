<div role="main">

<div id="section-intro" class="section">

## Behaviour Types Module

This module implements the BaseBehaviour class extensions. These
subclasses are used to model the agent behaviours of various types.

</div>

<div class="section">

## Classes

  - `  class CompoundBehaviour (agent) `
    
    <div class="desc">
    
    This class models compound behaviours in PADE.
    
    CompoundBehaviour is an abstract class to model behaviours that
    handle other behaviours as sub-behaviours. This classe implements
    the general add\_subbehaviour(SimpleBehaviour) method that add
    simple behaviours in the local queue as sub-behaviours. The actions
    of this class need to be implemented in subclasses.
    
    ##### Attributes
    
      - **`_subbehaviours`** : `list`  
        The list of added subbehaviours.
    
    ##### Parameters
    
      - **`agent`** : `Agent`  
        The agent that holds the behaviour.
    
    </div>
    
    ##### Ancestors
    
      - pade.behaviours.base.BaseBehaviour
      - pade.behaviours.protocols.Behaviour
    
    ##### Subclasses
    
      - [SequentialBehaviour](#behaviours.types.SequentialBehaviour "behaviours.types.SequentialBehaviour")
    
    ##### Methods
    
      - `  def add_subbehaviour(self, behaviour) `
        
        <div class="desc">
        
        Adds sub-behaviours in this sub-behaviour local list.
        
        ##### Parameters
        
          - **`behaviour`** : `SimpleBehaviour`  
            The simple behaviour to be added as sub-behaviour.
        
        ##### Raises
        
          - `ValueError`  
            If the sub-behaviour not it a subclass from SimpleBehaviour.
        
        </div>
    
      - `  def receive(self, message) `
        
        <div class="desc">
        
        Passes the received message to the sub-behaviours.
        
        This method doesn't save the messages in the local queue, by
        default. If you want to change that behaviour, override this
        method in the subclasses.
        
        ##### Parameters
        
          - **`message`** : `ACLMessage`  
            The message to be passed to the sub-behaviours.
        
        ##### Raises
        
          - `ValueError`  
            If the passed object is not an ACLMessage.
        
        </div>

  - `  class CyclicBehaviour (agent) `
    
    <div class="desc">
    
    This class models an infinite behaviour.
    
    CyclicBehaviour are behaviours that executes its action() method
    until the end of the agent.
    
    ##### Parameters
    
      - **`agent`** : `Agent`  
        The agent which performs the behaviour.
    
    </div>
    
    ##### Ancestors
    
      - [SimpleBehaviour](#behaviours.types.SimpleBehaviour "behaviours.types.SimpleBehaviour")
      - pade.behaviours.base.BaseBehaviour
      - pade.behaviours.protocols.Behaviour
    
    ##### Subclasses
    
      - [TickerBehaviour](#behaviours.types.TickerBehaviour "behaviours.types.TickerBehaviour")
    
    ##### Methods
    
      - `  def done(self) `
        
        <div class="desc">
        
        Defines when the behaviour ends.
        
        This method always returns False and should not be overridden in
        the subclasses. By returning False, the behaviour will execute
        indefinitely.
        
        </div>
    
    ##### Inherited members
    
      - `SimpleBehaviour`:
          - `action`
          - `add_lock`
          - `lock`
          - `set_return`
          - `wait_return`

  - `  class OneShotBehaviour (agent) `
    
    <div class="desc">
    
    This class models a finite behaviour.
    
    OneShotBehaviour are behaviours that executes its action() method
    only once.
    
    ##### Parameters
    
      - **`agent`** : `Agent`  
        The agent which performs the behaviour.
    
    </div>
    
    ##### Ancestors
    
      - [SimpleBehaviour](#behaviours.types.SimpleBehaviour "behaviours.types.SimpleBehaviour")
      - pade.behaviours.base.BaseBehaviour
      - pade.behaviours.protocols.Behaviour
    
    ##### Subclasses
    
      - [WakeUpBehaviour](#behaviours.types.WakeUpBehaviour "behaviours.types.WakeUpBehaviour")
    
    ##### Methods
    
      - `  def done(self) `
        
        <div class="desc">
        
        Defines when the behaviour ends.
        
        This method always returns True and should not be overridden in
        the subclasses. By returning True, the behaviour will execute
        only once.
        
        </div>
    
    ##### Inherited members
    
      - `SimpleBehaviour`:
          - `action`
          - `add_lock`
          - `lock`
          - `set_return`
          - `wait_return`

  - `  class SequentialBehaviour (agent) `
    
    <div class="desc">
    
    This class models the sequential-compound behaviours in PADE.
    
    SequentialBehaviour models a sequential-compound behaviour. This
    classe adds SimpleBehaviour and its subclasses as sub-behaviours,
    and execute them sequentially. The execution order is defined as the
    sub-behavious are added. No overrides are required for this class.
    
    ##### Parameters
    
      - **`agent`** : `Agent`  
        The agent that holds the behaviour.
    
    </div>
    
    ##### Ancestors
    
      - [CompoundBehaviour](#behaviours.types.CompoundBehaviour "behaviours.types.CompoundBehaviour")
      - pade.behaviours.base.BaseBehaviour
      - pade.behaviours.protocols.Behaviour
    
    ##### Methods
    
      - `  def action(self) `
        
        <div class="desc">
        
        This method performs the actions of the behaviour.
        
        This method executes sequentially the sub-behaviours. This
        method should not be overridden in the subclasses.
        
        </div>
    
      - `  def done(self) `
        
        <div class="desc">
        
        Defines when the behaviour ends.
        
        This method always returns True and should not be overridden in
        the subclasses. By returning True, the behaviour will execute
        only once.
        
        </div>
    
    ##### Inherited members
    
      - `CompoundBehaviour`:
          - `add_subbehaviour`
          - `receive`

  - `  class SimpleBehaviour (agent) `
    
    <div class="desc">
    
    Class that implements the SimpleBehaviour.
    
    SimpleBehaviour class models a basic behaviour. The action() method
    must be overridden in the subclasses to define the behaviour
    actions. The done() method must indicate (by returning True) when
    this behaviour will finalize.
    
    ##### Attributes
    
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
    
      - pade.behaviours.base.BaseBehaviour
      - pade.behaviours.protocols.Behaviour
    
    ##### Subclasses
    
      - [CyclicBehaviour](#behaviours.types.CyclicBehaviour "behaviours.types.CyclicBehaviour")
      - [OneShotBehaviour](#behaviours.types.OneShotBehaviour "behaviours.types.OneShotBehaviour")
    
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
        
        This method can be overridden in the subclasses.
        
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
        
        This method must be overridden in the subclasses, defining
        exactly when the behaviour will ends (by returning True).
        
        </div>
    
      - `  def set_return(self, data) `
        
        <div class="desc">
        
        Sets the return for this behaviour.
        
        ##### Parameters
        
          - **`data`** : `object`  
            The data to be returned by the behaviour.
        
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

  - `  class TickerBehaviour (agent, time) `
    
    <div class="desc">
    
    This class models an infinite behaviour that waits a timeout before
    performs its actions.
    
    TickerBehaviour class models an infinite behaviour that always waits
    a timeout before execute its actions. The actions of this class must
    be implemented into the on\_tick() method.
    
    ##### Attributes
    
      - **`time`** : `float`  
        The amount of time (in seconds) to be waited before each
        execution of the behaviour.
    
    ##### Parameters
    
      - **`agent`** : `Agent`  
        The agent that executes the behaviour.
      - **`time`** : `float`  
        The amount of time (in seconds) to be waited before each
        execution of the behaviour.
    
    </div>
    
    ##### Ancestors
    
      - [CyclicBehaviour](#behaviours.types.CyclicBehaviour "behaviours.types.CyclicBehaviour")
      - [SimpleBehaviour](#behaviours.types.SimpleBehaviour "behaviours.types.SimpleBehaviour")
      - pade.behaviours.base.BaseBehaviour
      - pade.behaviours.protocols.Behaviour
    
    ##### Methods
    
      - `  def action(self) `
        
        <div class="desc">
        
        This method performs the actions of the behaviour.
        
        This method should not be overridden in the subclasses. Use the
        method on\_tick() to write the actions of this behaviour.
        
        </div>
    
      - `  def on_tick(self) `
        
        <div class="desc">
        
        An abstract method that performs the actions of the behaviour.
        
        This method can be overridden in the subclasses.
        
        </div>
    
    ##### Inherited members
    
      - `CyclicBehaviour`:
          - `add_lock`
          - `done`
          - `lock`
          - `set_return`
          - `wait_return`

  - `  class WakeUpBehaviour (agent, time) `
    
    <div class="desc">
    
    This class models a finite behaviour that waits a timeout before
    performs its actions.
    
    WakeUpBehaviour class models a finite behaviour that executes its
    actions after a timeout. The actions of this class must be
    implemented into the on\_wake() method.
    
    ##### Attributes
    
      - **`time`** : `float`  
        The amount of time (in seconds) to be waited before the
        behaviour performs its actions.
    
    ##### Parameters
    
      - **`agent`** : `Agent`  
        The agent that executes the behaviour.
      - **`time`** : `float`  
        The amount of time (in seconds) to be waited before the
        behaviour performs its actions.
    
    </div>
    
    ##### Ancestors
    
      - [OneShotBehaviour](#behaviours.types.OneShotBehaviour "behaviours.types.OneShotBehaviour")
      - [SimpleBehaviour](#behaviours.types.SimpleBehaviour "behaviours.types.SimpleBehaviour")
      - pade.behaviours.base.BaseBehaviour
      - pade.behaviours.protocols.Behaviour
    
    ##### Methods
    
      - `  def action(self) `
        
        <div class="desc">
        
        This method performs the actions of the behaviour.
        
        This method should not be overridden in the subclasses. Use the
        method on\_wake() to write the actions of this behaviour.
        
        </div>
    
      - `  def on_wake(self) `
        
        <div class="desc">
        
        An abstract method that performs the actions of the behaviour.
        
        This method can be overridden in the subclasses.
        
        </div>
    
    ##### Inherited members
    
      - `OneShotBehaviour`:
          - `add_lock`
          - `done`
          - `lock`
          - `set_return`
          - `wait_return`

</div>

# Index

<div class="toc">

  - [Behaviour types module](#behaviour-types-module)

</div>

  - ### Super-module
    
      - `behaviours`

  - ### [Classes](#classes)
    
      - #### `CompoundBehaviour`
        
          - `add_subbehaviour`
          - `receive`
    
      - #### `CyclicBehaviour`
        
          - `done`
    
      - #### `OneShotBehaviour`
        
          - `done`
    
      - #### `SequentialBehaviour`
        
          - `action`
          - `done`
    
      - #### `SimpleBehaviour`
        
          - `action`
          - `add_lock`
          - `done`
          - `lock`
          - `set_return`
          - `wait_return`
    
      - #### `TickerBehaviour`
        
          - `action`
          - `on_tick`
    
      - #### `WakeUpBehaviour`
        
          - `action`
          - `on_wake`

</div>

Generated by [pdoc 0.8.1](https://pdoc3.github.io/pdoc).