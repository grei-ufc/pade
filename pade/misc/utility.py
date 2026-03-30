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
        Method to display message in the console.
    """
    date = datetime.now()
    date = date.strftime('%d/%m/%Y %H:%M:%S.%f')[:-3]
    click.echo(click.style('[{}] {} --> '.format(name, date), fg='green') + str(data))
    # print('[' + name + '] ' + date + str(data))


def call_in_thread(method, *args):
    """
        Call blocking method in another thread
    """
    reactor.callInThread(method, *args)


def call_later(time, method, *args):
    """
        Call method in reactor thread after timeout
    """
    return reactor.callLater(time, method, *args)


def defer_to_thread(block_method, result_method, *args):
    """
        Call blocking method in another thread passing callback
    """
    d = threads.deferToThread(block_method, *args)
    d.addCallback(result_method)


def call_from_thread(method, *args):
    """
        Call reactor method (usually not thread safe) from thread
    """
    reactor.callFromThread(method, *args)


def start_loop(agents):
    """Start reactor thread main loop"""
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

def format_message_content(content, max_len=100):
    """
    Enhanced version that ensures ALL binary data is safely formatted for display.
    """
    # If it is None
    if content is None:
        return "[None]"
    
    # If it is a string
    if isinstance(content, str):
        # Checks if it looks like binary data encoded as a string
        if any(ord(c) > 127 for c in content[:50]):
            return "[Binary data encoded as string]"
        if len(content) > max_len:
            return content[:max_len] + "..."
        return content
    
    # If it is bytes (binary data like pickle)
    if isinstance(content, bytes):
        try:
            # Tries to decode as UTF-8 first
            decoded = content.decode('utf-8', errors='replace')
            # If it has many control characters, it's likely a pickle object
            control_chars = sum(1 for c in decoded[:50] if ord(c) < 32 and c not in '\n\r\t')
            if control_chars > 10:
                # It is likely a pickle
                try:
                    import pickle
                    data = pickle.loads(content)
                    if isinstance(data, dict):
                        if 'ams' in str(data) or len(data) > 1:
                            return f"[Agent Table: {len(data)} agents]"
                        return f"[Dictionary: {len(data)} keys]"
                    elif isinstance(data, list):
                        return f"[Serialized list: {len(data)} items]"
                    else:
                        return f"[Serialized data: {type(data).__name__}]"
                except:
                    return f"[Bytes: {len(content)} bytes]"
            else:
                # It is valid UTF-8 text
                return decoded[:max_len] + "..." if len(decoded) > max_len else decoded
        except:
            # If decoding fails, tries to identify if it's a pickle
            try:
                import pickle
                data = pickle.loads(content)
                if isinstance(data, dict):
                    if 'ams' in str(data):
                        return f"[Agent Table: {len(data)} agents]"
                    return f"[Dictionary: {len(data)} keys]"
                elif isinstance(data, list):
                    return f"[Serialized list: {len(data)} items]"
                else:
                    return f"[Serialized data: {type(data).__name__}]"
            except:
                # If it's not a pickle, shows generic info
                return f"[Bytes: {len(content)} bytes]"
    
    # If it is a dictionary (already deserialized)
    if isinstance(content, dict):
        if 'ams' in str(content):
            return f"[Agent Table: {len(content)} agents]"
        return f"[Dictionary: {len(content)} keys]"
    
    # If it is a list
    if isinstance(content, (list, tuple)):
        return f"[{type(content).__name__}: {len(content)} items]"
    
    # Other types
    return f"[{type(content).__name__}]"