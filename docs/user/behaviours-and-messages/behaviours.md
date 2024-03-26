﻿# Behaviours in PADE
##### PADE Update (LAAI | UFPA), released at 4-22-2019, updated at 5-27-2020



## Content
- [Introduction](#introduction)
- [Agent behaviours on PADE](#agent-behaviours-on-pade)
	- [OneShotBehaviour class](#oneshotbehaviour-class)
	- [WakeUpBehaviour](#wakeupbehaviour-class)
	- [SimpleBehaviour](#simplebehaviour-class)
	- [CyclicBehaviour](#cyclicbehaviour-class)
	- [TickerBehaviour](#tickerbehaviour-class)
	- [SequentialBehaviour](#sequentialbehaviour-class)
- [Behaviour return feature](#behaviour-return-feature)
- [Mutual Exclusion with behaviours](#mutual-exclusion-with-behaviours)
- [Contact us](#contact-us)


## Introduction
This document aims to describe how PADE implements behaviours of agents. The way to implement behaviours in PADE is similar to the paradigm used in [JADE Framework](https://jade.tilab.com/). This is an update provide to PADE by [LAAI](http://www.laai.ufpa.br/). Although this update is incorporated in the code, the features of the previous version of PADE still work normally. We hope you enjoy this update.


## Agent Behaviours on PADE
In this session we will approach quickly the referred way to program behaviours in PADE. The used paradigm is based in [JADE](https://jade.tilab.com/) programming, so, if you want to know more about this agent-based programming style, see some examples with behaviours in JADE.

The first thing to keep in mind while developing behaviours is that behaviours have two main methods to be implemented. They are the `action()` and `done()` methods.

The `action()` method is the most important to be implemented, because is it that will perform the actions of the behaviour (consequently, of the agent). All "hard code" of behaviour must be put on `action()` method.

Next, the `done()` method must implements the end of the behaviour. In other words, it must to tells to PADE when a behaviour finishes its actions. This method must returns a `bool`, which indicates whether a behaviour is ended (by returning `True`), or not (by returning `False`). There are cases where you don't need to implement this method, because it is predefined, as we will see later.

To better understand how PADE executes behaviours actions, the diagram below synthesis the behaviours cycle within PADE scheduler.

![Behaviours life cycle diagram on PADE](../../img/behaviours_lifecycle.png)

At each execution, a behaviour will perform its `action()` method, executing soon after its `done()` method. If the `done()` method returns `False`, the behaviour will be executed again; if the `done()` method returns `True`, the behaviour will execute its `on_end()` method and, then, it will ends. The `on_end()` method can be overridden to execute post-execution actions. It is useful for signalizes when a behaviour ended or clear control structures used in the behaviour execution.

Basically, behaviours may be of two types: finite behaviours or infinite behaviours. They do exactly what their names mean, that is, finite behaviors end at a definite time (its `done()` method will return `True` at some time) and infinite behaviors never end (its `done()` method never returns `True`). The classes in PADE that implement the finite behaviours are `OneShotBehaviour` and `WakeUpBehaviour`. In its turn, the classes that implement the infinite behaviours are `CyclicBehaviour` and`TickerBehaviour`. All of them are subclasses from the `SimpleBehaviour` class, which is a general model to implement behaviours that run alone. On the other hand, the `SequentialBehaviour` class is a subclass of the `CompoundBehaviour` class, which models a special type of behaviour that manage several sub-behaviours.

To further explain the features of the behaviours classes in PADE, we will see each one of them separately in the next sub-sessions.

### OneShotBehaviour class
The `OneShotBehaviour` is a class that models finite behaviours. This is a `SimpleBehaviour` subclass whose main characteristic is that its `done()` method always returns `True`, ending the behaviour soon after its first execution. Let's look at an example by writing a `OneShotBehaviour` that makes an agent says "hello world".

```python
# Needed imports
from pade.behaviours.types import OneShotBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop

# Defining the HelloWorldAgent (inherits from Agent class)
class HelloWorldAgent(Agent):

	# This method will execute at agent startup
	def setup(self):
		# This adds the 'SayHello' behaviour in the agent
		self.add_behaviour(SayHello(self))


# Defining the SayHello behaviour
class SayHello(OneShotBehaviour):

	# This method executes the main actions of SayHello behaviour
	def action(self):
		# This shows a message, with date/hour information, in console
		display_message(self.agent, 'Hello world!')


# This starts the agent HelloWorldAgent with PADE
if __name__ == '__main__':
	# Defining a HelloWorldAgent object
	helloagent = HelloWorldAgent('hello')
	# Creating a list with agents that will be executed
	agents_list = [helloagent]
	# Passing the agent list to main loop of PADE
	start_loop(agents_list)
```
First, we defined the `HelloWorldAgent`. Next, we described what the agent will execute in its startup. The method `Agent.setup()` defines what the agent will execute when started. Usually we use this method to attach to agent any behaviour that the agent needs to execute first. In its turn, the `Agent.add_behaviour(BaseBehaviour)` method is used to attach a behaviour to be executed by an agent.

> Note: The `BaseBehaviour` class is the basic class from which all other behaviours inherit from, that is, it is the general type of any behavior classes.

After writing the agent, we defined the `SayHello` behaviour. The only method needed to be implemented is the `SayHello.action()`. This method defines the **action** that the agent will takes when performs this behaviour. To `OneShotBehaviour` no other method is needed to be implemented.

The last lines deal with the initiation of the agents within PADE's loop. While instantiating new agents, we need to give to they unique names. These names are passed to Agent `__init__()` under string form or by using an `AID` object. The `start_loop(list)` function receives a list of agents that will be executed on PADE. To start the agents, execute `pade start-runtime file_name.py` on a terminal and enjoy it! 0\/

### WakeUpBehaviour class
The `WakeUpBehaviour` also implements a finite behaviour, with the important difference that this behaviour will wait for a time before perform its actions. Another important spot to focus is that this class implements its actions on `on_wake()` method, rather `action()` method. We can see an example below that models an agent which waits by 5 seconds to makes an ask.

``` python
# Needed imports
from pade.behaviours.types import WakeUpBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop

# Defining the LaterAgent (inherits from Agent class)
class LateAgent(Agent):

	# This method will execute at agent startup
	def setup(self):
		# The behaviour is created with two args, where
		# the second is a time (in seconds) to behaviour
		# waits.
		behaviour = AmILate(self, 5)
		# This adds a behaviour in the agent
		self.add_behaviour(behaviour)


# Defining the AmILate behaviour
class AmILate(WakeUpBehaviour):

	# This method executes the main actions of behaviour
	def on_wake(self):
		display_message(self.agent, 'Am I late?')


# This starts the agents with PADE
if __name__ == '__main__':
	# Defining a LateAgent object
	lateagent = LateAgent('late')
	# Creating a list with agents that will be executed
	agents_list = [lateagent]
	# Passing the agent list to main loop of PADE
	start_loop(agents_list)
```
Now, executing the `pade start-runtime file_name.py` command in the terminal, we will see the agent waiting 5 seconds before prints the ask "Am I late?" in the screen. This task is performed only once because it is a finite behaviour.

### SimpleBehaviour class
The `SimpleBehaviour` class is the simplest pre-implemented behaviour model in PADE (oh, really?). "Simple" means that you must program the `action()` and `done()` methods. The advantage of this behaviour model is that you can customize its end. Below there is an example where an agent counts and shows in console a counting from 1 to 10.

``` python
from pade.behaviours.types import SimpleBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display, start_loop

class CounterAgent(Agent):
	def setup(self):
		self.add_behaviour(Count(self))

class Count(SimpleBehaviour):
	# Defining initial parameters to behaviour
	def __init__(self, agent):
		# This call to superclass is needed, passing the agent
		super().__init__(agent)
		# Defining counting variable
		self.counter = 1

	def action(self):
		display(self.agent, 'Counting #%d' % self.counter)
		self.counter += 1

	# This method indicates when the behaviour finishes.
	def done(self):
		if self.counter > 10:
			# The behaviour will dies when True is returned
			return True
		return False

	# This method is executed when the behaviour dies x_x
	def on_end(self):
		display(self.agent, 'Counting finished.')

if __name__ == '__main__':
	start_loop([CounterAgent('counter')])
```
This code will create an agent to count from 1 to 10. When the `CounterAgent.counter` variable reach the value 10, the `done()` method will return `True`, finishing the behaviour. We also used the `on_end()` method to signalizes when the counting is ended. 

### CyclicBehaviour class
This is a class that implements a infinite behaviours. The main difference between this class and those that implement finite behaviours is that the `done()` method of this class always returns `False`, never ending. The cyclic classes have a close relation with behaviours blocking and messages receiving , but it will be explained in the next docs.

Now, we will see an example of an agent that models a clock and shows a message every 1 second.

``` python
from pade.behaviours.types import CyclicBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop

class TicTacAgent(Agent):
	def setup(self):
		self.add_behaviour(NoiseBehaviour(self))

class NoiseBehaviour(CyclicBehaviour):
	def action(self):
		display_message(self.agent, 'Tic-tac!')
		self.wait(1) # The behaviour will sleep by 1 second

if __name__ == '__main__':
	tic = TicTacAgent('tictac')
	start_loop([tic])
```
There is not much difference between this code and the codes shown above, except that the `CyclicBehaviour` will execute indefinitely. Moreover, is common to use **blocking** and **waiting** methods with cyclic behaviours, like the `wait(float)` method. This method will block the behaviour until the time argument provided in `timeout` ends. It is useful, in our example, to make `TicTacAgent` shows messages within a limit of time (one second, like a clock).

### TickerBehaviour class
This is the other class that implements infinite behaviours. Like `WakeUpBehaviour`, objects from this class will wait a timeout before execute its actions. The difference between the classes is that the `TickerBehaviour` will execute indefinitely. It is important to highlight that the method that implements actions on this class is the `on_tick()` method, rather `action()`.

We will remake the clock example, now using the `TickerBehaviour` class. The code follows below.

``` python
from pade.behaviours.types import TickerBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop

class TicTacAgent(Agent):
	def setup(self):
		self.add_behaviour(NoiseBehaviour(self, 1))

class NoiseBehaviour(TickerBehaviour):
	def on_tick(self):
		display_message(self.agent, 'Tic-tac!')

if __name__ == '__main__':
	start_loop([TicTacAgent('tictac')])
```

### SequentialBehaviour class
This is the most different class implementing behaviours in PADE. All behaviours in PADE are scheduled parallel, however, sometimes is necessary perform behaviours in a sequential mode. The `SequentialBehaviour` class is a `CompoundBehaviour` subclass which implements sequential behaviours by adding sub-behaviours. All sub-behaviour of this class must to be a `SimpleBehaviour` or its subclasses. The sub-behaviours are added one by one, following an order, which defines the order that the behaviours will be executed. 

Unlike simple behaviours, a `SequentialBehaviour` doesn't require implementation for the `action()` method. You just have to add this behaviour to an agent and it will run its sub-behaviours. The example below shows the usage of this class.

``` python
from pade.behaviours.types import OneShotBehaviour, SequentialBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display, start_loop

class SequentialAgent(Agent):
	def setup(self):
		# Defining the sequential behaviour
		sequential = SequentialBehaviour(self)
		# Adding sub-behaviours into 'sequential'
		sequential.add_subbehaviour(Count1_10(self))
		sequential.add_subbehaviour(Count11_20(self))
		sequential.add_subbehaviour(Count21_30(self))
		# Adding 'sequential' into agent
		self.add_behaviour(sequential)

# Behaviour that counts from 1 to 10
class Count1_10(OneShotBehaviour):
	def action(self):
		for num in range(1,11):
			display(self.agent, num)

# Behaviour that counts from 11 to 20
class Count11_20(OneShotBehaviour):
	def action(self):
		for num in range(11,21):
			display(self.agent, num)

# Behaviour that counts from 21 to 30
class Count21_30(OneShotBehaviour):
	def action(self):
		for num in range(21,31):
			display(self.agent, num)

# Starting loop
if __name__ == '__main__':
	start_loop([SequentialAgent('seq')])
```

In the code above, we used the `add_subbehaviour(BaseBehavior)` method to add three different `OneShotBehaviour` to perform a counting. We can add any `SimpleBehaviour` subclass as sub-behaviour of `sequential` object. The order of addition shown above defined the execution order of `sequential` sub-behaviours. To test, try to swap the order of addition of the sub-behaviours in `sequential` and see what happens with your counting.

Finally, we used the `Agent.add_behaviour(BaseBehaviour)` method to add the `sequential` object to the agent. At this moment, the `sequential` behaviour will execute all of its sub-behaviours.


> Note: You can add any `SimpleBehaviour` subclass as `SequentialBehaviour` sub-behaviour, however, if you add an infinite behaviour, the `SequentialBehaviour` never will ends as well. Take it into account when developing your system.



## Behaviour return feature
While you're developing a small multiagent system, the features described above will probably meet all of your needs. Each agent has defined roles and performs a small number of tasks.

However, the world is cruel and, when you're developing more difficult things, in practice, you will see your code tends to be a mess. You will note that the agents will keep them roles, but many of the small tasks that they perform are the same. At this time, you will feel you are writing the same code again and again. This is a disaster!

To deal with cases like these, PADE provides the behaviour return feature. This feature is similar to function return in Python, however, it is implemented using two methods of the `SimpleBehaviour` class (and subclasses): the methods `set_return(data)` and `wait_return()`. Programmatically speaking, this feature implements a thread synchronization, where one thread (a behaviour) waits for the return by another thread (another behaviour).

To understand how these methods works, lets see a general code. Let's assume that `behaviour_a` has a reference to `behaviour_b`. Let's assume also that `behaviour_a` has a `say(str)` method that shows a message in the screen.

``` python
# Code in behaviour_a
behaviour_a.say('The message is: %s' % behaviour_a.wait_return(behaviour_b))
```

The `behaviour_a` executes the method `wait_return()` which calls the return of `behaviour_b`, provided as an argument. At this time, the `behaviour_a` will block and wait for the `behaviour_b`'s return. Let's assume that the following code is executed in `behaviour_b`:

``` python
# Code in behaviour_b
behaviour_b.set_returns('Use Linux. <3')
```

When `behaviour_b` executes the above line, the string `'Use Linux <3'` is returned to `behaviour_a`. At this time, the `behaviour_a` will resume its execution and print the message in the screen.

The behaviour return feature provides the possibility to share behaviours between different agents. This feature allows the programmer to place recurrent code in one behaviour that can be executed by any agent that performs that actions. In addition to avoid code repetition, the behaviour return feature favors the modularization and the code organization.

Let's see the behaviour return feature working in one example. The example below models agents that choose trips within certain criteria. There are two types of agents: the hurried agents (that choose the shortest trips) and the economic agents (that choose the cheapest trips). Note when the behaviour return is used in the code.

``` python
from pade.behaviours.types import WakeUpBehaviour, OneShotBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display, start_loop
import random


# HurriedPassenger Agent
class HurriedPassenger(Agent):
	def __init__(self, aid, start_time, destination, trips):
		super().__init__(aid)
		self.destination = destination
		self.trips = trips
		self.start_time = start_time

	def setup(self):
		self.add_behaviour(ChooseShortestTrip(self, self.start_time))

class ChooseShortestTrip(WakeUpBehaviour):
	def on_wake(self):
		display(self.agent, 'I started to choose the trips.')
		# Creates a behaviour instance
		selected_trips = FilterDestination(self.agent)
		# Adds it in the agent
		self.agent.add_behaviour(selected_trips)
		# Here this behaiviour will block and wait for the 
		# `selected_trips` return
		trips = self.wait_return(selected_trips)
		# After the return, we will choose the shortest trip among
		# the returned trips
		if trips == []:
			display(self.agent, 'There is no trips available to %s.' % self.agent.destination)
		else:
			shortest = 0
			for i in range(1, len(trips)):
				if trips[i]['time'] < trips[shortest]['time']:
					shortest = i
			display(self.agent, 'I chose this trip:')
			print('-', trips[shortest])


# EconomicPassenger Agent
class EconomicPassenger(Agent):
	def __init__(self, aid, start_time, destination, trips):
		super().__init__(aid)
		self.destination = destination
		self.trips = trips
		self.start_time = start_time

	def setup(self):
		self.add_behaviour(ChooseCheapestTrip(self, self.start_time))

class ChooseCheapestTrip(WakeUpBehaviour):
	def on_wake(self):
		display(self.agent, 'I started to choose the trips.')
		# Creates a behaviour instance
		selected_trips = FilterDestination(self.agent)
		# Adds it in the agent
		self.agent.add_behaviour(selected_trips)
		# Here this behaiviour will block and wait for the 
		# `selected_trips` return
		trips = self.wait_return(selected_trips)
		# After the return, we will choose the cheapest trip among
		# the returned trips
		if trips == []:
			display(self.agent, 'There is no trips available to %s.' % self.agent.destination)
		else:
			cheapest = 0
			for i in range(1, len(trips)):
				if trips[i]['price'] < trips[cheapest]['price']:
					cheapest = i
			display(self.agent, 'I chose this trip:')
			print('-', trips[cheapest])


class FilterDestination(OneShotBehaviour):
	def action(self):
		selection = list()
		# Select the trips with the correct destination
		for trip in self.agent.trips:
			if trip['destination'] == self.agent.destination:
				selection.append(trip)
		display(self.agent, 'I got the trips for %s.' % self.agent.destination)
		# Sets the selected trips able to be returned
		self.set_return(selection)


if __name__ == '__main__':
	trips = list()
	# Randomly creates the buses destinations
	for number in range(700, 720):
		trips.append({
			'number': number,
			'destination': random.choice(['Belém', 'Recife', 'Teresina', 'Fortaleza']),
			'time' : random.randint(20, 35),
			'price' : random.randint(180, 477) + round(random.random(), 2)
		})
	# Prints the entire trips list
	print('The available trips are:')
	for trip in trips:
		print('-', trip)
	# Initiating loop with the passed agents
	agents = list()
	agents.append(HurriedPassenger('hurried-a', 0, 'Belém', trips))
	agents.append(HurriedPassenger('hurried-b', 2, 'Teresina', trips))
	agents.append(HurriedPassenger('hurried-c', 4, 'Fortaleza', trips))
	agents.append(EconomicPassenger('economic-a', 6, 'Recife', trips))
	agents.append(EconomicPassenger('economic-b', 8, 'Belém', trips))
	agents.append(EconomicPassenger('economic-c', 10, 'Fortaleza', trips))
	start_loop(agents)
```

Run the command `pade start-runtime example_name.py` and watch the magic happens. Note that there are different agents performing different actions, having different roles, but sharing the same `FilterDestination` behaviour.  Both type of agents have a common task which is abstracted into a shared behaviour. This is the main contribution of this feature.

You may say "couldn't you solve this problem using just methods or functions?". I answer yes, I could. However, we can see that in large projects with many behaviours and many agents, use foreign behaviour methods may cause confusion in the development. By encapsulating a common action in a single behaviour, you can easily share a behaviour among as many agents as you want.



## Mutual Exclusion with behaviours
At some point in your programmer's life, you may need a behaviour to perform certain activity that another behaviour should not perform at the same time. This is possible to occurs, as the behaviours in PADE are executed in parallel by default. You can suggest me to use the `SequentialBehaviour`, that can solve the most of the problems like this, but it may not fit all cases. The `SequentialBehaviour` executes one behaviour at a time, and this may not be what you want.

When you want to run two or more behaviours of the same agent simultaneously, and also want they synchronize their activities, the mutual exclusion may fit your need. The main idea of mutual exclusion is establish points of code to be executed without interference from other behaviours. It may be useful when you want to ensure that a shared resource (a variable, an object, a file, or another resource) is accessed synchronously by the behaviours of the same or different agent. It may be used also when you want to switch between different roles that an agent can assume throughout its life cycle.

To deal with that, we will need to handle an object from the class `Lock` of the `threading` module. We must create an object from this class and pass it to all the behaviours that we want to synchronize. Besides that, we need to specify which point of the code will stay locked and unlocked. This point is called critical section.

To pass the `Lock` object to the desired behaviours, we must use the `add_lock(lock)` method from the`SimpleBehaviour` class and subclasses. We can use two different ways to indicate the critical section: the `with` Python statement in the `lock` object, or the `acquire()` and `release()` methods from the class `Lock`. To see how these methods work, refer to the `threading.Lock` [documentation](https://docs.python.org/3/library/threading.html#threading.Lock). To illustrate, we will see examples that use the both ways to do the mutual exclusion. 

Programmatically speaking, when a behaviour enters its critical section (by entering the `with` statement or executing the `acquire()` method), it checks if another behaviour already holds the lock. If so, the behaviour will block until the other behaviour releases the lock. The release is done when the behaviour leaves its critical section (by leaving the `with` statement or executing the `release()` method). When the lock is free, the behaviour that was waiting holds the lock and any other behaviour will be unable to execute its critical section as well.

If you want to know more about how the `Lock` class works, see the Python threading module documentation [here](https://docs.python.org/3/library/threading.html#lock-objects).

To clear our thinking, we will see two usage examples of behaviours with mutual exclusion: one using the `acquire()` and `release()` `Lock` methods; other using the `with` statement. First, we will rewrite the counting example implemented with `SequentialBehaviour` class. Note the critical sections.

``` python
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
		# Here starts the critical section (holds the lock)
		self.lock.acquire()
		display(self.agent, 'Now, I will count from 1 to 10 slowly:')
		for num in range(1,11):
			display(self.agent, num)
			self.wait(1) # I put this so that we can see the behaviours blocking
		# Here ends the critical section (releases the lock)
		self.lock.release()

# Behaviour that counts from 11 to 20
class Count11_20(OneShotBehaviour):
	def action(self):
		# Here starts the critical section (holds the lock)
		self.lock.acquire()
		display(self.agent, 'Now, I will count from 11 to 20 slowly:')
		for num in range(11,21):
			display(self.agent, num)
			self.wait(1)
		# Here ends the critical section (releases the lock)
		self.lock.release()

# Behaviour that counts from 21 to 30
class Count21_30(OneShotBehaviour):
	def action(self):
		# Here starts the critical section (holds the lock)
		self.lock.acquire()
		display(self.agent, 'Now, I will count from 21 to 30 slowly:')
		for num in range(21,31):
			display(self.agent, num)
			self.wait(1)
		# Here ends the critical section (releases the lock)
		self.lock.release()


if __name__ == '__main__':
	start_loop([Sequential('seq')])
```

Running the above code, you will see the same results of the `SequentialBehaviour` approach. Although the results are the same, instead of the behaviours execute one after the other, the behaviours are executed in parallel. However, the critical section of each one was executed one at a time, thanks to the mutual exclusion. Try to remove the critical section points to see what happens with the behaviours. ;)

To make sure that the mutual exclusion really works, lets to see another example. Probably our results will be pretty different, once the threads scheduling is different in our hardware and OS. Even so, the code below aims to show us how the mutual exclusion works when many behaviours tries to hold the lock at the same time.

``` python
from pade.behaviours.types import CyclicBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display, start_loop
import threading


class MutualExclusionAgent(Agent):
	def setup(self):
		# Creating a Lock object
		lock = threading.Lock()
		# Creating the behaviours
		say_biscoito = SayBiscoito(self)
		say_bolacha = SayBolacha(self)
		# Passing the same lock object to behaviours
		say_bolacha.add_lock(lock)
		say_biscoito.add_lock(lock)
		# Adding the behaviours in the agent
		self.add_behaviour(say_biscoito)
		self.add_behaviour(say_bolacha)

class SayBiscoito(CyclicBehaviour):
	def action(self):
		# Defines the entire critical section
		with self.lock:
			for _ in range(5): # The agent will hold the lock by 5 prints
				display(self.agent, 'The correct name is "BISCOITO".')
				self.wait(0.5)

class SayBolacha(CyclicBehaviour):
	def action(self):
		# Defines the entire critical section
		with self.lock:
			# Here the agent will hold the lock only by 1 print, and 
			# release it right away
			display(self.agent, '"BOLACHA" is the correct name.')


if __name__ == '__main__':
	start_loop([MutualExclusionAgent('mea')])
```

Run the above code and watch the results. Note that the `SayBiscoito` behaviour holds the lock and prints 5 times its phrase. Afterward, it releases the lock and tries to hold it again. If the `SayBolacha` behaviour can hold the lock first, it prints its phrase by 1 time and releases the lock right away. These two behaviours will continue to disputate the same lock for the eternity. All the times that `SayBiscoito` gets the lock, it will print by 5 times, while the `SayBolacha` will print by once. The `SayBiscoito` never will print 4 or 6 times, because its critical section holds the lock exactly by 5 times.

> **Important note:** keep in mind that mutual exclusion can generate problems with deadlock, even in distributed systems. Then, use it with some software engineering to avoid problems. ;)



## Contact us
All the presented code examples can be found at the `pade/examples/behaviours-and-messages/` directory of this repository.

If you find a bug or need any specific help, feel free to visit us or submit an _issue_ on [GitHub](https://github.com/grei-ufc/pade). We appreciate contributions to make PADE better. ;)


>Written by [@italocampos](https://github.com/italocampos) with [StackEdit](https://stackedit.io/).

---

[Universidade Federal do Pará](https://portal.ufpa.br)  
[Laboratory of Applied Artificial Intelligence](http://www.laai.ufpa.br)
Instituto de Ciências Exatas e Naturais  
Faculdade de Computação  
Belém-PA, Brasil  

[Universidade Federal do Ceará](http://www.ufc.br/)  
[Grupo de Redes Elétricas Inteligentes](https://github.com/grei-ufc)  
Fortaleza-CE, Brasil