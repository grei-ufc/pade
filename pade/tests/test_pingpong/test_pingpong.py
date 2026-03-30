#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PADE ping-pong communication test.

Supported modes:
- Integrated mode via `pade start-runtime --port <base_port> test_pingpong.py`
- Manual mode via `python test_pingpong.py <ping|pong> <port> [target_port]`
"""

import sys

from pade.misc.utility import display_message, start_loop, format_message_content
from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.misc.data_logger import get_shared_session_id, logger

class PingAgent(Agent):
    """Agente que envia mensagens PING periódicas"""
    
    def __init__(self, aid, pong_port):
        super().__init__(aid=aid, debug=False)
        self.pong_port = pong_port
        self.ping_count = 0
        self.pong_received = 0
        
    def on_start(self):
        super().on_start()
        print("\n" + "="*50)
        print("🏓 AGENTE PING INICIADO")
        print(f"📡 Enviando PINGs para porta: {self.pong_port}")
        print("="*50 + "\n")
        
        # Schedule the first PING after 5 seconds.
        self.call_later(5.0, self.send_ping)
    
    def send_ping(self):
        """Envia uma mensagem PING para o agente PONG"""
        self.ping_count += 1
        
        # Constrói nome do agente PONG
        pong_name = f'pong_{self.pong_port}@localhost:{self.pong_port}'
        
        print(f"\n🚀 Enviando PING #{self.ping_count}")
        print(f"   ➡️ Destino: {pong_name}")
        
        # Cria mensagem
        message = ACLMessage(ACLMessage.INFORM)
        message.add_receiver(AID(name=pong_name))
        message.set_content(f'PING #{self.ping_count} from {self.aid.name}')
        message.set_conversation_id(f'ping_conversation_{self.ping_count}')
        
        # Envia
        self.send(message)
        print(f"   ✅ PING #{self.ping_count} enviado!")
        
        # Schedule the next PING in 30 seconds.
        self.call_later(30.0, self.send_ping)
    
    def react(self, message):
        """Processa mensagens recebidas"""
        super().react(message)
        
        # Usa a função de formatação para exibição segura
        formatted_content = format_message_content(message.content)
        
        # Verifica se é uma resposta PONG
        if message.performative == ACLMessage.INFORM and 'PONG' in str(message.content):
            self.pong_received += 1
            print(f"\n🎉 PONG RECEBIDO!")
            print(f"   📨 De: {message.sender.name}")
            print(f"   📝 Conteúdo: {formatted_content}")
            print(f"   📊 Estatísticas: PONGs recebidos: {self.pong_received}/{self.ping_count}")
        
        # Mensagens de sistema (tabela de agentes, etc)
        elif message.system_message:
            # Verifica se é atualização de tabela (mensagem binária)
            if isinstance(message.content, bytes) or 'Table update' in str(formatted_content):
                print(f"📋 Tabela de agentes atualizada")
            else:
                print(f"📋 Mensagem de sistema: {message.performative} - {formatted_content}")


class PongAgent(Agent):
    """Agente que responde mensagens PING com PONG"""
    
    def __init__(self, aid):
        super().__init__(aid=aid, debug=False)
        self.pongs_sent = 0
        self.pings_received = 0
        
    def on_start(self):
        super().on_start()
        print("\n" + "="*50)
        print("🏸 AGENTE PONG INICIADO")
        print(f"📡 Aguardando PINGs na porta {self.aid.port}")
        print("="*50 + "\n")
    
    def react(self, message):
        """Processa mensagens recebidas e responde com PONG"""
        super().react(message)
        
        # Usa a função de formatação para exibição segura
        formatted_content = format_message_content(message.content)
        
        # Verifica se é um PING
        if message.performative == ACLMessage.INFORM and 'PING' in str(message.content):
            self.pings_received += 1
            print(f"\n🏓 PING RECEBIDO!")
            print(f"   📨 De: {message.sender.name}")
            print(f"   📝 Conteúdo: {formatted_content}")
            
            # Prepara resposta PONG
            reply = message.create_reply()
            reply.set_performative(ACLMessage.INFORM)
            reply.set_content(f'PONG #{self.pings_received} from {self.aid.name}')
            
            # Envia resposta
            self.pongs_sent += 1
            self.send(reply)
            print(f"   📤 PONG #{self.pongs_sent} enviado!")
            print(f"   📊 Estatísticas: PONGs enviados: {self.pongs_sent}")
        
        # Mensagens de sistema
        elif message.system_message:
            # Verifica se é atualização de tabela (mensagem binária)
            if isinstance(message.content, bytes) or 'Table update' in str(formatted_content):
                print(f"📋 Tabela de agentes atualizada")
            else:
                print(f"📋 Mensagem de sistema: {message.performative} - {formatted_content}")


def _print_usage():
    print("\n" + "=" * 60)
    print("🏓 TESTE DE COMUNICAÇÃO PING-PONG - PADE 3.12+")
    print("=" * 60)
    print("\nModo integrado:")
    print("  pade start-runtime --port 24000 test_pingpong.py")
    print("\nModo manual:")
    print("  python test_pingpong.py pong 37001")
    print("  python test_pingpong.py ping 37000 37001")
    print("=" * 60 + "\n")


def _run_integrated_mode(base_port):
    """Run both agents in a single integrated PADE runtime."""
    session_id = get_shared_session_id()
    logger.log_session(session_id=session_id, name="PingPong_Test", state="Started")

    pong_port = base_port
    ping_port = base_port + 1

    pong_name = f'pong_{pong_port}@localhost:{pong_port}'
    ping_name = f'ping_{ping_port}@localhost:{ping_port}'

    print("\n" + "=" * 60)
    print("🏓 TESTE DE COMUNICAÇÃO PING-PONG - PADE 3.12+")
    print("=" * 60)
    print(f"\n🏸 Integrated PONG agent on port {pong_port}")
    print(f"🚀 Integrated PING agent on port {ping_port} -> PONG on port {pong_port}")
    print("-" * 60)

    agents = [
        PongAgent(AID(name=pong_name)),
        PingAgent(AID(name=ping_name), pong_port),
    ]

    for agent in agents:
        agent.update_ams({'name': 'localhost', 'port': 8000})

    display_message('System', '🏓 Starting integrated ping-pong test...')
    start_loop(agents)


def _run_manual_mode():
    """Run a single ping or pong agent with explicit command line arguments."""
    if len(sys.argv) < 3:
        _print_usage()
        sys.exit(1)

    agent_type = sys.argv[1]

    if agent_type not in ['ping', 'pong']:
        print(f"\n❌ ERRO: Tipo de agente inválido: '{agent_type}'. Use 'ping' ou 'pong'")
        sys.exit(1)

    try:
        port = int(sys.argv[2])
    except ValueError:
        print(f"\n❌ ERRO: Porta inválida: '{sys.argv[2]}'. Deve ser um número inteiro.")
        sys.exit(1)

    if agent_type == 'ping':
        if len(sys.argv) < 4:
            print("\n❌ ERRO: Agente PING precisa da porta do PONG!")
            print("Uso correto: python test_pingpong.py ping <porta_ping> <porta_pong>")
            sys.exit(1)

        try:
            pong_port = int(sys.argv[3])
        except ValueError:
            print(f"\n❌ ERRO: Porta do PONG inválida: '{sys.argv[3]}'")
            sys.exit(1)

        agent_name = f'ping_{port}@localhost:{port}'
        agent = PingAgent(AID(name=agent_name), pong_port)
        print(f"\n🚀 Iniciando PING agent na porta {port} -> PONG na porta {pong_port}")

    else:
        agent_name = f'pong_{port}@localhost:{port}'
        agent = PongAgent(AID(name=agent_name))
        print(f"\n🏸 Iniciando PONG agent na porta {port}")

    print("-" * 50)
    agent.update_ams({'name': 'localhost', 'port': 8000})
    start_loop([agent])


if __name__ == '__main__':
    # Integrated runtime passes only the base port as argv[1].
    if len(sys.argv) == 2:
        try:
            base_port = int(sys.argv[1])
        except ValueError:
            _print_usage()
            sys.exit(1)

        _run_integrated_mode(base_port)
    else:
        _run_manual_mode()
