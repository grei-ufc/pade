''' This example shows how the behaviour return works. There are
hurried passengers looking for the shortest trips, and economic
passengers looking for the cheapest trip.
'''

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