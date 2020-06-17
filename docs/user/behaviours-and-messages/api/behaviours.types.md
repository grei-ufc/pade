<div role="main">

<div id="section-intro" class="section">

## Behaviour Types Module

This module implements the BaseBehaviour class extensions. These
subclasses are used to model the agent behaviours of various types.


</div>

<div class="section">

## Classes

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
    
      - pade.behaviours.core.BaseBehaviour
      - pade.behaviours.protocols.Behaviour
    
    ##### Subclasses
    
      - [TickerBehaviour](#behaviours.types.TickerBehaviour "behaviours.types.TickerBehaviour")
    
    ##### Methods
    
      - `  def action(self) `
        
        <div class="desc">
        
        An abstract method that performs the actions of the behaviour.
        
        This method can be overridden in the subclasses.
        
        </div>
    
      - `  def done(self) `
        
        <div class="desc">
        
        Defines when the behaviour ends.
        
        This method always returns False and should not be overridden in
        the subclasses. By returning False, the behaviour will execute
        indefinitely.
        
        </div>
<br>


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
    
      - pade.behaviours.core.BaseBehaviour
      - pade.behaviours.protocols.Behaviour
    
    ##### Subclasses
    
      - [SequentialBehaviour](#behaviours.types.SequentialBehaviour "behaviours.types.SequentialBehaviour")
      - [WakeUpBehaviour](#behaviours.types.WakeUpBehaviour "behaviours.types.WakeUpBehaviour")
    
    ##### Methods
    
      - `  def action(self) `
        
        <div class="desc">
        
        An abstract method that performs the actions of the behaviour.
        
        This method can be overridden in the subclasses.
        
        </div>
    
      - `  def done(self) `
        
        <div class="desc">
        
        Defines when the behaviour ends.
        
        This method always returns True and should not be overridden in
        the subclasses. By returning True, the behaviour will execute
        only once.
        
        </div>
<br>

  - `  class SequentialBehaviour (agent) `
    
    <div class="desc">
    
    This class models the sequential-compound behaviours in PADE.
    
    SequentialBehaviour models a sequential-compound behaviour. This
    classe adds other non-compound behaviours (like OneShotBehaviour or
    SimpleBehaviour) as sub-behaviours, and performs them sequentially.
    The execution order is defined as the sub-behavious are added. No
    overrides are required for this class.
    
    ##### Attributes
    
      - **`_subbehaviours`** : `list`  
        The list of added subbehaviours.
    
    ##### Parameters
    
      - **`agent`** : `Agent`  
        The agent that holds the behaviour.
    
    </div>
    
    ##### Ancestors
    
      - [OneShotBehaviour](#behaviours.types.OneShotBehaviour "behaviours.types.OneShotBehaviour")
      - pade.behaviours.core.BaseBehaviour
      - pade.behaviours.protocols.Behaviour
    
    ##### Methods
    
      - `  def action(self) `
        
        <div class="desc">
        
        This method performs the actions of the behaviour.
        
        This method executes sequentially the sub-behaviours. This
        method should not be overridden in the subclasses.
        
        </div>
    
      - `  def add_subbehaviour(self, behaviour) `
        
        <div class="desc">
        
        Adds sub-behaviours in this sub-behaviour local list.
        
        ##### Parameters
        
          - **`behaviour`** : `BaseBehaviour`  
            The behaviour to be added as sub-behaviour.
        
        </div>
    
      - `  def receive(self, message) `
        
        <div class="desc">
        
        Passes the received message to the sub-behaviours.
        
        ##### Parameters
        
          - **`message`** : `ACLMessage`  
            The message to be passed to the sub-behaviours.
        
        ##### Raises
        
          - `ValueError`  
            If the passed object is not an ACLMessage.
        
        </div>
    
    ##### Inherited members
    
      - `OneShotBehaviour`:
          - `done`
<br>
<br>

  - `  class SimpleBehaviour (agent) `
    
    <div class="desc">
    
    Class that implements the SimpleBehaviour.
    
    SimpleBehaviour class models a basic behaviour. The action() method
    must be overridden in the subclasses to define the behaviour
    actions. The done() method must indicate (by returning True) when
    this behaviour will finalize.
    
    ##### Parameters
    
      - **`agent`** : `Agent`  
        The agent which performs the behaviour.
    
    </div>
    
    ##### Ancestors
    
      - pade.behaviours.core.BaseBehaviour
      - pade.behaviours.protocols.Behaviour
    
    ##### Methods
    
      - `  def action(self) `
        
        <div class="desc">
        
        An abstract method that performs the actions of the behaviour.
        
        This method can be overridden in the subclasses.
        
        </div>
    
      - `  def done(self) `
        
        <div class="desc">
        
        Defines when the behaviour ends.
        
        This method must be overridden in the subclasses, defining
        exactly when the behaviour will ends (by returning True).
        
        </div>
<br>

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
      - pade.behaviours.core.BaseBehaviour
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
          - `done`
<br>
<br>

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
      - pade.behaviours.core.BaseBehaviour
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
          - `done`

</div>

# Index

<div class="toc">

  - [Behaviour types module](#behaviour-types-module)

</div>

  - ### Super-module
    
      - `behaviours`

  - ### [Classes](#header-classes)
    
      - #### `CyclicBehaviour`
        
          - `action`
          - `done`
    
      - #### `OneShotBehaviour`
        
          - `action`
          - `done`
    
      - #### `SequentialBehaviour`
        
          - `action`
          - `add_subbehaviour`
          - `receive`
    
      - #### `SimpleBehaviour`
        
          - `action`
          - `done`
    
      - #### `TickerBehaviour`
        
          - `action`
          - `on_tick`
    
      - #### `WakeUpBehaviour`
        
          - `action`
          - `on_wake`

</div>

Generated by [pdoc 0.8.1](https://pdoc3.github.io/pdoc).
