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

import click
import signal
import subprocess
import multiprocessing
import shlex
import time
import json
import datetime
import sys


class FlaskServerProcess(multiprocessing.Process):
    """
        This class implements the thread that executes
        the web server with Flask application.
    """

    secure = None

    def __init__(self, secure):
        self.secure = secure
        multiprocessing.Process.__init__(self)

    def run(self):
        from pade.web.flask_server import run_server
        run_server(self.secure)


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
interrupted = False


def run_config_file(ctx, param, value):

    if not value or ctx.resilient_parsing:
        return

    try:
        config = json.load(open(value))
    except FileNotFoundError:
        click.echo(click.style('Arquivo de configuração PADE não encontrado!', fg='red'))
        ctx.exit()

    main(config)
    ctx.exit()


def main(config):
    global interrupted

    click.clear()
    click.echo(click.style('''
        This is
         ____   _    ____  _____ 
        |  _ \ / \  |  _ \| ____|
        | |_) / _ \ | | | |  _|  
        |  __/ ___ \| |_| | |___ 
        |_| /_/   \_\____/|_____|
        
        Python Agent DEvelopment framework   
        ''', fg='green'))
    click.echo(click.style('''
        PADE is a free software under development by
        Electric Smart Grid Group - GREI
        Federal University of Ceara - UFC - Brazil

        https://github.com/grei-ufc/pade''', fg='blue'))

    agent_files = config.get('agent_files')
    if agent_files is None:
        click.echo(click.style('attribute agent_file is mandatory', fg='red'))
        return

    num = config.get('num')
    if num is None:
        num = 1

    port = config.get('port')
    if port is None:
        port = 2000

    secure = config.get('secure')

    processes = list()
    # -------------------------------------------------------------
    # inicializa o servico web de gerenciamento de agentes do PADE
    # -------------------------------------------------------------
    pade_web = config.get('pade_web')
    if pade_web is None:
        p = FlaskServerProcess(secure)
        p.daemon = True
        p.start()
        processes.append(p)
    else:
        if pade_web['active']:
            p = FlaskServerProcess(secure)
            p.daemon = True
            p.start()
            processes.append(p)
        else:
            pass
    
    # -------------------------------------------------------------
    # inicializa o banco de dados do PADE e o agente AMS
    # -------------------------------------------------------------
    session = config.get('session')
    pade_ams = config.get('pade_ams')

    from pade.core import new_ams

    if pade_ams is None:
        commands = 'python {} {} {} {} {}'.format(new_ams.__file__,
                                               session['username'],
                                               session['email'],
                                               session['password'],
                                               8000)
        if sys.platform == 'win32':
            commands = shlex.split(commands, posix=False)
        else:
            commands = shlex.split(commands)
        p = subprocess.Popen(commands, stdin=subprocess.PIPE)
        processes.append(p)
    else:
        if pade_ams['launch']:
            commands = 'python {} {} {} {} {}'.format(new_ams.__file__,
                                                   session['username'],
                                                   session['email'],
                                                   session['password'],
                                                   pade_ams['port'])
            if sys.platform == 'win32':
                commands = shlex.split(commands, posix=False)
            else:
                commands = shlex.split(commands)
            p = subprocess.Popen(commands, stdin=subprocess.PIPE)
            processes.append(p)

    # -------------------------------------------------------------
    # inicializa o agente Sniffer
    # -------------------------------------------------------------
    pade_sniffer = config.get('pade_sniffer')

    from pade.core import sniffer

    if pade_sniffer is None:
        time.sleep(2.0)
        commands = 'python {} {}'.format(sniffer.__file__,
                                         8001)
        if sys.platform == 'win32':
            commands = shlex.split(commands, posix=False)
        else:
            commands = shlex.split(commands)
        p = subprocess.Popen(commands, stdin=subprocess.PIPE)
        processes.append(p)
    else:
        if pade_sniffer['active']:
            time.sleep(2.0)
            commands = 'python {} {}'.format(sniffer.__file__,
                                             pade_sniffer['port'])
            if sys.platform == 'win32':
                commands = shlex.split(commands, posix=False)
            else:
                commands = shlex.split(commands)
            p = subprocess.Popen(commands, stdin=subprocess.PIPE)
            processes.append(p)   
        else:
            pass

    # -------------------------------------------------------------
    # inicializa os agentes PADE
    # -------------------------------------------------------------
    time.sleep(3.0)
    port_ = port
    for agent_file in agent_files:
        for i in range(num):
            commands = 'python {} {}'.format(agent_file, port_)
            if sys.platform == 'win32':
                commands = shlex.split(commands, posix=False)
            else:
                commands = shlex.split(commands)
            p = subprocess.Popen(commands, stdin=subprocess.PIPE)
            processes.append(p)
            time.sleep(0.5)
            port_ += 1 

    while True:
        time.sleep(2.0)
        
        if interrupted:
            click.echo(click.style('\nStoping PADE...', fg='red'))
            for p in processes:
                p.kill()
            break

@click.group()
def cmd():
    pass

@cmd.command()
@click.argument('agent_files', nargs=-1)
@click.option('--num', default=1)
@click.option('--port', default=2000)
@click.option('--secure', is_flag=True)
@click.option('--pade_ams/--no_pade_ams', default=True)
@click.option('--pade_web/--no_pade_web', default=True)
@click.option('--pade_sniffer/--no_pade_sniffer', default=True)
@click.option('--username', prompt='please enter a username', default='pade_user')
@click.option('--password', prompt=True, hide_input=True, default='12345')
@click.option('--config_file', is_eager=True, expose_value=False, callback=run_config_file)
def start_runtime(num, agent_files, port, secure, pade_ams, pade_web, pade_sniffer, username, password):
    config = dict()
    config['agent_files'] = agent_files
    config['num'] = num
    config['port'] = port
    config['secure'] = secure
    config['session'] = dict()
    config['session']['username'] = username
    config['session']['email'] = 'pade_user@pade.com'
    config['session']['password'] = password
    config['pade_ams'] = dict()
    config['pade_ams']['launch'] = True
    config['pade_ams']['host'] = 'localhost'
    config['pade_ams']['port'] = 8000
    config['pade_sniffer'] = dict()
    config['pade_sniffer']['active'] = pade_sniffer
    config['pade_sniffer']['host'] = 'localhost'
    config['pade_sniffer']['port'] = 8001
    config['pade_web'] = dict()
    config['pade_web']['active'] = pade_web
    config['pade_web']['host'] = 'localhost'
    config['pade_web']['port'] = 5000

    create_tables()
    main(config)


@cmd.command()
def create_pade_db():
    create_tables()


@cmd.command()
def drop_pade_db():
    click.echo(click.style('[...] Droping Pade tables in selected data base.', fg='red'))
    from pade.web.flask_server import db    
    db.drop_all()
    click.echo(click.style('[ok_] Tables droped in selected data base', fg='green'))


@cmd.command()
def start_web_interface():
    create_tables()
    click.echo(click.style('[...] Starting Flask web interface.', fg='red'))
    
    p = FlaskServerProcess()
    p.daemon = True
    p.start()

    while True:
        time.sleep(2.0)
        
        if interrupted:
            click.echo(click.style('\nStoping PADE...', fg='red'))
            p.kill()
            break

    click.echo(click.style('[ok_] Flask web interface stopped', fg='green'))


def create_tables():
    click.echo(click.style('[...] Creating Pade tables in selected data base.', fg='red'))
    from pade.web.flask_server import db
    db.create_all()
    click.echo(click.style('[ok_] Tables created in selected data base', fg='green'))