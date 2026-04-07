"""Framework for Intelligent Agents Development - PADE

The MIT License (MIT)

Copyright (c) 2019 Lucas S Melo
Copyright (c) 2026 Douglas Barros (Update & Migration)

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
import os
import signal
import subprocess
import time
import json
import datetime
import sys
from pathlib import Path


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
interrupted = False


def _resolve_python_executable():
    """Return the current interpreter to keep subprocesses in the same environment."""
    return sys.executable or "python"


def _resolve_agent_file(agent_file):
    """Resolve agent scripts relative to the current working directory when possible."""
    candidate = Path(agent_file)
    if candidate.exists():
        return str(candidate.resolve())
    return agent_file


def _launch_process(processes, args):
    """Launch a PADE subprocess and keep a reference for shutdown."""
    process = subprocess.Popen(args, stdin=subprocess.PIPE)
    processes.append(process)
    return process


def _context_requests_detailed(ctx):
    """Infer detailed runtime mode from the current command invocation."""
    raw_args = sys.argv[1:]
    command_name = getattr(getattr(ctx, "command", None), "name", "")
    detailed_flag = "--detailed" in raw_args and "--no-detailed" not in raw_args
    return detailed_flag or command_name in {"start-runtime-detailed", "start-runtimedetailed"}


def _build_runtime_config(num, agent_files, port, secure, pade_ams, pade_sniffer, username, password, detailed=False):
    """Build the integrated runtime configuration dictionary."""
    config = dict()
    config['agent_files'] = agent_files
    config['num'] = num
    config['port'] = port
    config['secure'] = secure
    config['detailed'] = detailed
    config['session'] = dict()
    config['session']['username'] = username
    config['session']['email'] = 'pade_user@pade.com'
    config['session']['password'] = password
    config['pade_ams'] = dict()
    config['pade_ams']['launch'] = pade_ams
    config['pade_ams']['host'] = 'localhost'
    config['pade_ams']['port'] = 8000
    config['pade_ams']['debug'] = detailed
    config['pade_sniffer'] = dict()
    config['pade_sniffer']['active'] = pade_sniffer
    config['pade_sniffer']['host'] = 'localhost'
    config['pade_sniffer']['port'] = 8001
    config['pade_sniffer']['debug'] = detailed
    return config


def run_config_file(ctx, param, value):

    if not value or ctx.resilient_parsing:
        return

    try:
        config = json.load(open(value))
    except FileNotFoundError:
        click.echo(click.style('PADE configuration file not found!', fg='red'))
        ctx.exit()

    config['detailed'] = bool(config.get('detailed', False) or _context_requests_detailed(ctx))

    main(config)
    ctx.exit()


def main(config):
    global interrupted

    click.clear()
    click.echo(click.style(r'''
        This is
         ____   _    ____  _____ 
        |  _ \ / \  |  _ \| ____|
        | |_) / _ \ | | | |  _|  
        |  __/ ___ \| |_| | |___ 
        |_| /_/   \_\____/|_____|
        
        Python Agent DEvelopment framework   
        ''', fg='green'))
    click.echo(click.style('''
        PADE is a free software under development by:

        - Electric Smart Grid Group - GREI
        Federal University of Ceara - UFC - Brazil
        
        - Laboratory of Applied Artificial Intelligence - LAAI
        Federal University of Para - UFPA

        https://github.com/grei-ufc/pade''', fg='blue'))

    agent_files = config.get('agent_files')
    if agent_files is None:
        click.echo(click.style('Attribute agent_file is mandatory', fg='red'))
        return

    num = config.get('num')
    if num is None:
        num = 1

    port = config.get('port')
    if port is None:
        port = 2000

    secure = config.get('secure')
    detailed = bool(config.get('detailed', False))

    processes = list()
    python_exec = _resolve_python_executable()
    click.echo(click.style('[info] Starting integrated runtime (AMS + Sniffer + agents)', fg='cyan'))
    if detailed:
        click.echo(click.style('[info] Detailed runtime traces enabled', fg='yellow'))

    # Initialize the CSV data logger before launching services so the runtime has a root session.
    init_data_logger(config)
    
    # -------------------------------------------------------------
    # Initialize the AMS agent
    # -------------------------------------------------------------
    session = config.get('session')
    pade_ams = config.get('pade_ams')

    from pade.core import new_ams

    if pade_ams is None:
        click.echo(click.style('[info] Starting AMS on localhost:8000', fg='blue'))
        ams_args = [
            python_exec,
            str(Path(new_ams.__file__).resolve()),
            session['username'],
            session['email'],
            session['password'],
            '8000',
        ]
        if detailed:
            ams_args.append('debug')
        _launch_process(
            processes,
            ams_args,
        )
    else:
        if pade_ams['launch']:
            click.echo(click.style(f"[info] Starting AMS on {pade_ams['host']}:{pade_ams['port']}", fg='blue'))
            ams_args = [
                python_exec,
                str(Path(new_ams.__file__).resolve()),
                session['username'],
                session['email'],
                session['password'],
                str(pade_ams['port']),
            ]
            if detailed:
                ams_args.append('debug')
            _launch_process(
                processes,
                ams_args,
            )

    # -------------------------------------------------------------
    # Initialize the Sniffer agent
    # -------------------------------------------------------------
    pade_sniffer = config.get('pade_sniffer')

    from pade.core import sniffer

    if pade_sniffer is None:
        time.sleep(2.0)
        click.echo(click.style('[info] Starting Sniffer on localhost:8001', fg='blue'))
        sniffer_args = [
            python_exec,
            str(Path(sniffer.__file__).resolve()),
            '8001',
        ]
        if detailed:
            sniffer_args.append('debug')
        _launch_process(
            processes,
            sniffer_args,
        )
    else:
        if pade_sniffer['active']:
            time.sleep(2.0)
            click.echo(click.style(f"[info] Starting Sniffer on {pade_sniffer['host']}:{pade_sniffer['port']}", fg='blue'))
            sniffer_args = [
                python_exec,
                str(Path(sniffer.__file__).resolve()),
                str(pade_sniffer['port']),
            ]
            if detailed:
                sniffer_args.append('debug')
            _launch_process(
                processes,
                sniffer_args,
            )
        else:
            click.echo(click.style('[info] Sniffer disabled for this runtime', fg='yellow'))

    # -------------------------------------------------------------
    # Initialize the PADE agents
    # -------------------------------------------------------------
    time.sleep(3.0)
    port_ = port
    for agent_file in agent_files:
        for i in range(num):
            resolved_agent_file = _resolve_agent_file(agent_file)
            click.echo(click.style(f'[info] Starting agent script: {resolved_agent_file} on base port {port_}', fg='blue'))
            _launch_process(
                processes,
                [
                    python_exec,
                    resolved_agent_file,
                    str(port_),
                ],
            )
            time.sleep(0.5)
            port_ += 1 

    while True:
        time.sleep(2.0)
        
        if interrupted:
            click.echo(click.style('\nStopping PADE...', fg='red'))
            for p in processes:
                p.kill()
            break


def init_data_logger(config):
    """Initialize a root runtime session for the integrated CLI."""
    from pade.misc.data_logger import logger
    
    # Create initial session log
    session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    os.environ["PADE_SESSION_ID"] = session_id
    config["runtime_session_id"] = session_id
    
    logger.log_session(
        session_id=session_id,
        name=f"Session_{session_id}",
        state="started"
    )
    
    # Log the initialization event
    logger.log_event(
        event_type="runtime_started",
        data=config
    )
    
    click.echo(click.style(f'[ok_] Data logging started (CSV format)', fg='green'))
    click.echo(click.style(f'[info] Logs saved to: {logger.log_dir}', fg='blue'))
    return session_id


@click.group()
def cmd():
    pass


@cmd.command(name='start-runtime')
@click.argument('agent_files', nargs=-1)
@click.option('--num', default=1)
@click.option('--port', default=2000)
@click.option('--secure', is_flag=True)
@click.option('--pade_ams/--no_pade_ams', default=True)
@click.option('--pade_sniffer/--no_pade_sniffer', default=True)
@click.option('--detailed/--no-detailed', default=False, help='Show detailed AMS and Sniffer traces in the terminal.')
@click.option('--username', prompt='please enter a username', default='pade_user')
@click.option('--password', prompt=True, hide_input=True, default='12345')
@click.option('--config_file', is_eager=True, expose_value=False, callback=run_config_file)
def start_runtime(num, agent_files, port, secure, pade_ams, pade_sniffer, detailed, username, password):
    """Start AMS, Sniffer, and agent scripts in a single integrated runtime."""
    config = _build_runtime_config(
        num=num,
        agent_files=agent_files,
        port=port,
        secure=secure,
        pade_ams=pade_ams,
        pade_sniffer=pade_sniffer,
        username=username,
        password=password,
        detailed=detailed,
    )
    main(config)


@cmd.command(name='start-runtime-detailed')
@click.argument('agent_files', nargs=-1)
@click.option('--num', default=1)
@click.option('--port', default=2000)
@click.option('--secure', is_flag=True)
@click.option('--pade_ams/--no_pade_ams', default=True)
@click.option('--pade_sniffer/--no_pade_sniffer', default=True)
@click.option('--username', prompt='please enter a username', default='pade_user')
@click.option('--password', prompt=True, hide_input=True, default='12345')
@click.option('--config_file', is_eager=True, expose_value=False, callback=run_config_file)
def start_runtime_detailed(num, agent_files, port, secure, pade_ams, pade_sniffer, username, password):
    """Start the integrated runtime with detailed AMS and Sniffer traces."""
    config = _build_runtime_config(
        num=num,
        agent_files=agent_files,
        port=port,
        secure=secure,
        pade_ams=pade_ams,
        pade_sniffer=pade_sniffer,
        username=username,
        password=password,
        detailed=True,
    )
    main(config)


@cmd.command(name='start-runtimedetailed', hidden=True)
@click.argument('agent_files', nargs=-1)
@click.option('--num', default=1)
@click.option('--port', default=2000)
@click.option('--secure', is_flag=True)
@click.option('--pade_ams/--no_pade_ams', default=True)
@click.option('--pade_sniffer/--no_pade_sniffer', default=True)
@click.option('--username', prompt='please enter a username', default='pade_user')
@click.option('--password', prompt=True, hide_input=True, default='12345')
@click.option('--config_file', is_eager=True, expose_value=False, callback=run_config_file)
def start_runtime_detailed_legacy_alias(num, agent_files, port, secure, pade_ams, pade_sniffer, username, password):
    """Backward-compatible alias for the detailed integrated runtime."""
    config = _build_runtime_config(
        num=num,
        agent_files=agent_files,
        port=port,
        secure=secure,
        pade_ams=pade_ams,
        pade_sniffer=pade_sniffer,
        username=username,
        password=password,
        detailed=True,
    )
    main(config)


@cmd.command(name='show-logs')
def show_logs():
    """Displays information about the generated CSV logs."""
    from pade.misc.data_logger import logger
    
    click.echo(click.style('\n=== PADE Data Logs ===', fg='green'))
    click.echo(click.style(f'Log directory: {logger.log_dir}', fg='blue'))
    
    for log_file in logger.log_dir.glob('*.csv'):
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = sum(1 for _ in f) - 1  # Exclude header
            
            click.echo(click.style(f'{log_file.name}: {lines} entries', fg='yellow'))
    
    click.echo(click.style('Usage: pade export-logs <format> to export data', fg='blue'))


@cmd.command(name='export-logs')
@click.argument('format', type=click.Choice(['csv', 'json', 'txt']), default='csv')
def export_logs(format):
    """Exports logs to different formats."""
    from pade.misc.data_logger import logger
    import shutil
    import csv
    import json
    import datetime
    
    # Creates specific subfolders for each format (e.g., logs/exports/json/)
    export_dir = logger.log_dir / 'exports' / format
    export_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    exported_count = 0
    
    for log_file in logger.log_dir.glob('*.csv'):
        if log_file.exists():
            export_file = export_dir / f'{log_file.stem}_{timestamp}.{format}'
            
            # CSV: Exact backup copy
            if format == 'csv':
                shutil.copy2(log_file, export_file)
                
            # JSON: Structured object for APIs and Data Science
            elif format == 'json':
                data = []
                with open(log_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        data.append(row)
                
                with open(export_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
            
            # TXT: Human-readable report format
            elif format == 'txt':
                with open(log_file, 'r', encoding='utf-8') as f_in:
                    reader = csv.DictReader(f_in)
                    with open(export_file, 'w', encoding='utf-8') as f_out:
                        f_out.write(f"=== PADE LOG EXPORT: {log_file.stem.upper()} ===\n")
                        f_out.write(f"Generated at: {timestamp}\n\n")
                        
                        for i, row in enumerate(reader, 1):
                            f_out.write(f"--- Entry {i} ---\n")
                            for key, value in row.items():
                                f_out.write(f"{key}: {value}\n")
                            f_out.write("\n")
            
            click.echo(click.style(f'Exported: {export_file}', fg='green'))
            exported_count += 1
    
    if exported_count > 0:
        click.echo(click.style(f'\n[ok_] All {format.upper()} logs exported to: {export_dir}', fg='blue'))
    else:
        click.echo(click.style(f'\n[info] No CSV logs found in {logger.log_dir} to export.', fg='yellow'))


@cmd.command()
def version():
    """Shows the PADE version."""
    try:
        from importlib.metadata import version as get_version
        version = get_version("pade")
    except Exception:
        version = "2.2.6"
    
    click.echo(click.style(f'PADE version: {version}', fg='green'))
    click.echo(click.style('Python 3.12+ compatible (no Flask/SQLAlchemy)', fg='blue'))


@cmd.command(name='clean-logs')
def clean_logs():
    """Removes all log files (CSV and exports)."""
    from pade.misc.data_logger import logger
    import shutil
    
    log_dir = logger.log_dir
    
    # Check if the directory exists before trying to delete
    if not log_dir.exists():
        click.echo(click.style(f'\n[info] The directory {log_dir} does not exist. No logs to clean.', fg='yellow'))
        return
    
    click.echo(click.style(f'\nWarning: This will permanently delete all CSV files and the exports folder in {log_dir}', fg='yellow'))
    
    # click.confirm creates the (y/n) prompt automatically. abort=True cancels if the user says 'n'
    if click.confirm('Are you sure you want to proceed?', abort=True):
        try:
            shutil.rmtree(log_dir)
            click.echo(click.style(f'\n[ok_] Logs directory ({log_dir}) successfully deleted!', fg='green'))
        except Exception as e:
            click.echo(click.style(f'\n[error] Error deleting logs: {e}', fg='red'))
