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
"""

#from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Protocol
from pade.acl.messages import ACLMessage
import pickle

class PeerProtocol(Protocol):
    """docstring for PeerProtocol"""

    message = None
    mosaik_msg_id = None
    await_gen = None

    def __init__(self, fact):
        self.fact = fact

    def connectionMade(self):
        peer = self.transport.getPeer()
        sended_message = None

        for message in self.fact.messages:
            if int(message[0].port) == int(peer.port):
                if str(message[0].host) == 'localhost' and str(peer.host) == '127.0.0.1' or \
                   str(message[0].host) == str(peer.host):
                    self.send_message(pickle.dumps(message[1]))
                    sended_message = message
                    break
        if sended_message is not None:
            self.fact.messages.remove(sended_message)

    def connectionLost(self, reason):
        if self.message is not None:
            try:
                message = pickle.loads(self.message)
            except:
                print('Message not understood')
                print(self.message)
                return
            return message

    def dataReceived(self, data):
        # receives part of the sent message.
        if self.message is not None:
            self.message += data
        else:
            self.message = data
        # ------------------------------------
        # make a verification if the message
        # is a MOSAIK message
        # ------------------------------------
        header = int.from_bytes(self.message[:4], byteorder='big')
        if header == len(self.message[4:]):
            # get mosaik connection for assync
            if self.fact.agent_ref.mosaik_connection is None:
                self.fact.agent_ref.mosaik_connection = self

            # recebe o gerador retornado pelo método _process_message()
            gen = self.fact.agent_ref.mosaik_sim._process_message(self.message,
                                                                  self.mosaik_msg_id)

            # o gerador retornado por _process_message é ativado
            try:
                message = next(gen)
            except StopIteration as e:
                message = e.value

            # se o valor retornado pelo gerador for uma mensagem
            # no padrão Mosaik, isso é, não é nem um inteiro, nem
            # um valor None, então a mensagem é transmitida para 
            # o Mosaik
            if message is not None and not isinstance(message, int):
                self.transport.write(message)
                self.message = None
            else:
                # Caso a variável self.mosaik_msg_id não tenha o valor
                # None, significa que ela está armazenando o ID da 
                # mensagem step que originou a requisição assíncrona
                # e que o método step() está aguardando a finalização
                # da mensagem assíncrona. Entrar neste if significa
                # que a resposta da requisição assíncrona foi recebida
                if self.mosaik_msg_id:
                    try:
                        message = next(self.await_gen)    
                    except StopIteration as e:
                        message = e.value
                    if message is not None:
                        self.transport.write(message)
                        self.message = None
                        self.mosaik_msg_id = None
                        self.await_gen = None
                else:
                    # Caso o valor retornado por _process_message()
                    # seja um inteiro, representando o ID da mensagem
                    # Mosaik que está pausada aguardando o resultado
                    # da requisição assíncrona, esse valor é armazenado
                    # na variável self.mosaik_msg_id, e o gerador que retornou
                    # este valor é armazenado na variável self.await_gen
                    self.mosaik_msg_id = message
                    self.await_gen = gen
                    self.message = None

    def got_mosaik_message(self, message):
        self.transport.write(message)

    def send_message(self, message):
        l = len(message)
        if l > 1024:

            while len(message) > 0:
                message, m = message[1024:], message[:1024]
                self.transport.write(m)
        else:
            self.transport.write(message)

        try:
            self.transport.loseConnection()
        except:
            pass
