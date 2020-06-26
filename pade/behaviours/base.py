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

Behaviours module
-----------------

This module implements the base of the Behaviours classes, in order to enable
the PADE Scheduler to manage the agent behaviours.

@author: Italo Campos
"""

from pade.behaviours.protocols import Behaviour
from pade.acl.messages import ACLMessage
import queue, time

class BaseBehaviour(Behaviour):
	''' The basic behaviour class.

	This class inherits from Behaviour class and implements the basic methods
	for scheduled behaviours.
	'''

	def action(self):
		''' An abstract method that performs the actions of the behaviour.

		This method must be overridden in the subclasses.
		'''

		pass


	def done(self):
		''' Defines when the behaviour ends.

		This method must be overridden in the subclasses.
		'''

		pass


	def wait(self, timeout):
		''' Sleeps a behaviour until occurs a timeout.

		Parameters
		----------
		timeout : float
			The time to be waited.
		'''

		time.sleep(timeout)


	def on_end(self):
		''' Executes the final actions of the behaviou.

		The scheduler will call this method after the behaviour ends. May be
		overriden in subclasses.
		'''

		pass