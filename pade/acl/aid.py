#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Framework para Desenvolvimento de Agentes Inteligentes PADE

# The MIT License (MIT)

# Copyright (c) 2015 Lucas S Melo

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import random

class AID(object):
    def __init__(self, name=None, addresses=None, resolvers=None, userDefinedProperties=None):
        """
        Agent Identifier Class
        Optional parameters:
                String name with the form: localname@myAdress:port
                String[] addresses
                String[] resolvers
                ContentObject co
        """

        if name is not None:
            if '@' in name:
                self.name = name
                self.localname, adress = self.name.split('@')
                self.addresses = [adress]
                if ':' in adress:
                    self.host, self.port = adress.split(':')
                    self.port = int(self.port)
                else:
                    self.host, self.port = None, None
            else:
                self.localname = name
                self.host = 'localhost'
                self.port = random.randint(1024, 64024)
                self.name = self.localname + '@' + self.host +  ':'  + str(self.port) 
                self.addresses = [self.host + ':' + str(self.port)]
        else:
            self.name = None  # string
        if resolvers is not None:
            self.resolvers = resolvers
        else:
            self.resolvers = list()  # AID
        if userDefinedProperties is not None:
            self.userDefinedProperties = userDefinedProperties
        else:
            self.userDefinedProperties = list()  # properties

    def getName(self):
        """
        returns name of the agent (string)
        """
        return self.name
    
    def getLocalName(self):
        '''
        returns the localname of the agent
        '''
        return self.localname
    
    def setLocalName(self, name):
        """
        sets local name of the agent (string)
        """
        self.localname = name
        self.name = self.localname + '@' + self.host + ':' + str(self.port)
            
    def getHost(self):
        """
        gets host of the agent (string)
        """
        return self.host
    
    def setHost(self, host):
        """
        sets host of the agent (string)
        """
        self.host = host
        self.name = self.localname + '@' + self.host + ':' + str(self.port)
        
    def getPort(self):
        """
        gets port of the agent (string)
        """
        return self.port
    
    def setPort(self, port):
        """
        sets port of the agent (string)
        """
        self.port = port
        self.name = self.localname + '@' + self.host + ':' + str(self.port)
    
    def getAddresses(self):
        """
        returns a list of addreses
        """
        return self.addresses

    def addAddress(self, addr):
        """
        adds a new address to the addresses list
        """
        self.addresses.append(addr)

    def getResolvers(self):
        """
        returns a list of resolvers
        """
        return self.resolvers

    def addResolvers(self, resolver):
        """
        adds a new resolver to the resolvers list
        """
        self.resolvers.append(resolver)

    def getProperties(self):
        return self.userDefinedProperties

    def addProperty(self, prop):
        self.userDefinedProperties.append(prop)

    def match(self, other):
        """
        returns True if two AIDs are similar
        else returns False
        """

        if other is None:
            return True

        if (self.getName() is not None and other.getName() is not None
                and not (other.getName() in self.getName())):
            return False
        if (len(self.getAddresses()) > 0 and len(other.getAddresses()) > 0):
            for oaddr in other.getAddresses():
                found = False
                for saddr in self.getAddresses():
                    if (oaddr in saddr):
                        found = True
                if not found:
                    return False
        if (len(self.getResolvers()) > 0 and len(other.getResolvers()) > 0):
            for oaddr in other.getResolvers():
                found = False
                for saddr in self.getResolvers():
                    if (oaddr in saddr):
                        found = True
                if not found:
                    return False
        if (len(self.getProperties()) > 0 and len(other.getProperties()) > 0):
            for oaddr in other.getProperties():
                found = False
                for saddr in self.getProperties():
                    if (oaddr in saddr):
                        found = True
                if not found:
                    return False
        return True

    def __eq__(self, other):
        """
        Comparision operator (==)
        returns True if two AIDs are equal
        else returns False
        """
        if other is None:
            return False

        if (self.getName() is not None and other.getName() is not None
                and self.getName() != other.getName()):
            return False
        addr1 = self.getAddresses()
        addr2 = other.getAddresses()
        addr1.sort()
        addr2.sort()
        if addr1 != addr2:
            return False

        res1 = self.getResolvers()
        res2 = other.getResolvers()
        res1.sort()
        res2.sort()
        if res1 != res2:
            return False

        return True

    def __ne__(self, other):
        """
        != operator
        returns False if two AIDs are equal
        else returns True
        """

        return not (self == other)

    def __hash__(self):
        h = hash(self.name)
        for i in self.addresses:
            h = h + hash(i)
        for i in self.resolvers:
            h = h + hash(i)
        for i in self.userDefinedProperties:
            h = h + hash(i)
        return h

    def __str__(self):
        """
        returns a printable version of an AID
        """
        sb = ""
        if self.getName() is not None:
            sb = sb + ":name " + str(self.getName()) + "\n"
        if self.getAddresses() != []:
            sb = sb + ":addresses \n(sequence\n"
            for i in self.getAddresses():
                sb = sb + str(i) + '\n'
            sb = sb + ")\n"
        if self.getResolvers() != []:
            sb = sb + ":resolvers \n(sequence\n"
            for i in self.getResolvers():
                sb = sb + str(i) + '\n'
            sb = sb + ")\n"
        if sb != "":
            sb = "(agent-identifier\n" + sb + ")\n"
        else:
            sb = "None"

        return sb

    def as_xml(self):
        """
        returns a printable version of an AID in XML
        """
        sb = "<agent-identifier>\n\t" + self.encodeTag("name", self.getName()) + "\n"
        sb = sb + "\t<addresses>\n"

        addresses = self.getAddresses()
        for addr in addresses:
            sb = sb + "\t\t" + self.encodeTag("url", addr) + "\n"

        sb = sb + "\t</addresses>\n"

        sb = sb + "</agent-identifier>\n"

        return sb

    def encodeTag(self, tag, content):
        """
        encodes a content between 2 XML tags using the tag parameter

                <tag>content</tag>

        return string
        """
        sb = "<" + tag + ">" + content + "</" + tag + ">"

        return sb

if __name__ == '__main__':
    
    agentname = AID('lucas')
    print agentname.getName()
    print agentname.getHost()
    print agentname.getPort()
    print agentname.as_xml()
    print agentname.__str__()