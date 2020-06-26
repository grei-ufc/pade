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
        Method do display a message in the console.
    """
    date = datetime.now()
    date = date.strftime('%d/%m/%Y %H:%M:%S.%f')[:-3]
    try:
        click.echo(click.style('[{}] {} --> '.format(name.aid.getName(), date), fg='green') + str(data))
    except AttributeError:
        click.echo(click.style('[{}] {} --> '.format(name, date), fg='green') + str(data))
    # print('[' + name + '] ' + date + str(data))

def display(agent, message):
    ''' This function shows a message in PADE console without date and hour
    information.

    Parameters
    ----------
    agent : Agent
        The agent which prints the message in the screen.
    message : str
        The message to be printed in the screen.
    '''
    
    click.echo(click.style('[{}] --> '.format(agent.aid.getName()), fg='green') + str(message))

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


def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('%s |%s| %s%% %s' % (prefix, bar, percent, suffix))
    # Print New Line on Complete
    # if iteration == total:
    #     print()
