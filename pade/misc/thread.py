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

Thread-safe module
------------------

This module implements the basis of the thread-safe resources of PADE. This
module depends on the default Python threading library.

@author: Italo Campos
"""

import threading, copy

class SharedProperty(object):
    ''' The basic class for properties shared between concurrent behaviours.

    This class models the properties that are shared between concurrent
    behaviours and provides methods to avoid inconsistent data while handling
    the property throughout the execution of the system.
    

    Attributes
    ----------
    _data : object
        The data of the property to be handled by this class.
    _lock : threading.Lock
        The Lock object to be used in the thread-safe operations.
    '''

    def __init__(self, data = None):
        '''
        Parameters
        ----------
        data : object, optional
            The data to be handled by this class.
        '''

        self._data = data
        self._lock = threading.Lock()
    

    @property
    def lock(self):
        ''' Returns the local lock object
        
        Used to implement customized locks outside this class.

        Returns
        -------
        threading.Lock
            The lock object of this class.
        '''

        return self._lock
    

    @property
    def data(self):
        ''' Returns the data stored within the object
        
        Used only to manipulate the data within a lock context.

        Returns
        -------
        object
            The data stored within the object.
        '''

        return copy.deepcopy(self._data)
    

    @data.setter
    def data(self, data):
        ''' Sets the data within the object to the provided data
        
        Used only to manipulate the data within a lock context.

        Parameters
        ----------
        object
            The data to be added within the object.
        '''

        self._data = copy.deepcopy(data)


    def read(self):
        ''' Returns the data of the property

        Returns
        -------
        object
            The data stored inside this object.
        '''

        with self.lock:
            return self.data
    

    def write(self, data):
        ''' Writes the provided data inside this object.

        Parameters
        ----------
        data : object
            The data to be wiritten inside this object.
        '''

        with self.lock:
            self.data = data
    

    def __str__(self):
        ''' Overrides the __str__ method.

        Returns
        -------
        str
            The formated string of the stored data.
        '''

        return str(self.data)