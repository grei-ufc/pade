import click
import signal
import subprocess
import multiprocessing
import shlex
import time
import json
import datetime

from pade.core import new_ams
from pade.core import sniffer


class FlaskServerProcess(multiprocessing.Process):
    """
        This class implements the thread that executes
        the web server with Flask application.
    """
    def __init__(self):
        multiprocessing.Process.__init__(self)

    def run(self):
        from pade.web.flask_server import run_server
        run_server()


def signal_handler(signal, frame):
    global interrupted
    interrupted = True

signal.signal(signal.SIGINT, signal_handler)
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

    processes = list()
    # -------------------------------------------------------------
    # inicializa o serviço web de gerenciamento de agentes do PADE
    # -------------------------------------------------------------
    pade_web = config.get('pade_web')
    if pade_web is None:
        p = FlaskServerProcess()
        p.daemon = True
        p.start()
        processes.append(p)
    else:
        if pade_web['active']:
            p = FlaskServerProcess()
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
    if pade_ams is None:
        commands = 'python {} {} {} {}'.format(new_ams.__file__,
                                               session['username'],
                                               session['email'],
                                               session['password'])
        commands = shlex.split(commands)
        p = subprocess.Popen(commands, stdin=subprocess.PIPE)
        processes.append(p)
    else:
        commands = 'python {} {} {} {}'.format(new_ams.__file__,
                                               session['username'],
                                               session['email'],
                                               session['password'])
        commands = shlex.split(commands)
        p = subprocess.Popen(commands, stdin=subprocess.PIPE)
        processes.append(p)

    # -------------------------------------------------------------
    # inicializa o agente Sniffer
    # -------------------------------------------------------------
    pade_sniffer = config.get('pade_sniffer')
    if pade_sniffer is None:
        time.sleep(2.0)
        commands = 'python {}'.format(sniffer.__file__)
        commands = shlex.split(commands)
        p = subprocess.Popen(commands, stdin=subprocess.PIPE)
        processes.append(p)
    else:
        if pade_sniffer['active']:
            time.sleep(2.0)
            commands = 'python {}'.format(sniffer.__file__)
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



@click.command()
@click.argument('agent_files', nargs=-1)
@click.option('--num', default=1)
@click.option('--port', default=2000)
@click.option('--pade_ams/--no_pade_ams', default=True)
@click.option('--pade_web/--no_pade_web', default=True)
@click.option('--pade_sniffer/--no_pade_sniffer', default=True)
@click.option('--username', prompt='please enter a username', default='pade_user')
@click.option('--password', prompt=True, hide_input=True, default='12345')
@click.option('--config_file', is_eager=True, expose_value=False, callback=run_config_file)
def cmd(num, agent_files, port, pade_ams, pade_web, pade_sniffer, username, password):

    config = dict()
    config['agent_files'] = agent_files
    config['num'] = num
    config['port'] = port
    config['session'] = dict()
    config['session']['username'] = username
    config['session']['email'] = 'pade_user@pade.com'
    config['session']['password'] = password
    config['pade_ams'] = dict()
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

    main(config)
