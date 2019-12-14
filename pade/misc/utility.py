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

from twisted.internet import reactor, threads

from datetime import datetime
import click

def display_message(name, data):
    """
        Method do displsy message in the console.
    """
    date = datetime.now()
    date = date.strftime('%d/%m/%Y %H:%M:%S.%f')[:-3]
    click.echo(click.style('[{}] {} --> '.format(name, date), fg='green') + str(data))
    # print('[' + name + '] ' + date + str(data))


def call_in_thread(method, *args):
    reactor.callInThread(method, *args)


def call_later(time, method, *args):
    return reactor.callLater(time, method, *args)

def defer_to_thread(block_method, result_method, *args):
    d = threads.deferToThread(block_method, *args)
    d.addCallback(result_method)

def start_loop(agents):
    reactor.suggestThreadPoolSize(30)
    for agent in agents:
        agent.update_ams(agent.ams)
        agent.on_start()
        ILP = reactor.listenTCP(agent.aid.port, agent.agentInstance)
        agent.ILP = ILP
    reactor.run()
