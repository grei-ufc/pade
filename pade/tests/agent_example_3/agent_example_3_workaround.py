#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo de Requisição FIPA-Request - Workaround Corrigido
"""

from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID
from pade.behaviours.protocols import FipaRequestProtocol, TimedBehaviour
from pade.misc.data_logger import logger
from datetime import datetime
from sys import argv

class CompRequest(FipaRequestProtocol):
    def __init__(self, agent):
        super().__init__(agent=agent, message=None, is_initiator=False)

    def handle_request(self, message):
        super().handle_request(message)
        display_message(self.agent.aid.localname, '✅ Requisição recebida')
        
        now = datetime.now()
        reply = message.create_reply()
        reply.set_performative(ACLMessage.INFORM)
        current_time = now.strftime('%d/%m/%Y - %H:%M:%S')
        reply.set_content(current_time)
        
        self.agent.send(reply)
        display_message(self.agent.aid.localname, f'📤 Resposta: {current_time}')


class TimeAgent(Agent):
    def __init__(self, aid):
        super().__init__(aid=aid, debug=False)  # <-- debug=False remove mensagens de depuração
        self.comport_request = CompRequest(self)
        self.behaviours.append(self.comport_request)
    
    def on_start(self):
        super().on_start()
        display_message(self.aid.name, '⏰ TimeAgent pronto')


class ClockAgent(Agent):
    def __init__(self, aid, time_agent_aid):
        super().__init__(aid=aid, debug=False)  # <-- debug=False remove mensagens de depuração
        self.time_agent_aid = time_agent_aid
        self.request_count = 0
        self._table_updated = False
    
    def on_start(self):
        super().on_start()
        display_message(self.aid.name, f'🕐 ClockAgent iniciado')
        
        # Aguarda um momento e depois adiciona o TimeAgent na tabela
        self.call_later(2.0, self.add_target_to_table)
        self.call_later(5.0, self.send_request)
    
    def add_target_to_table(self):
        """Adiciona manualmente o TimeAgent na tabela local."""
        if not self._table_updated:
            self.agentInstance.table[self.time_agent_aid.name] = self.time_agent_aid
            display_message(self.aid.name, f'✅ TimeAgent adicionado manualmente à tabela local')
            self._table_updated = True
    
    def send_request(self):
        self.request_count += 1
        
        # Verifica se o destino está na tabela antes de enviar
        if self.time_agent_aid.name in self.agentInstance.table:
            message = ACLMessage(ACLMessage.REQUEST)
            message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
            message.add_receiver(self.time_agent_aid)
            message.set_content('time')
            
            display_message(self.aid.name, f'📤 Enviando requisição #{self.request_count}')
            self.send(message)
        else:
            display_message(self.aid.name, f'⏳ TimeAgent ainda não disponível na tabela')
        
        # Agenda próxima requisição
        self.call_later(8.0, self.send_request)
    
    def react(self, message):
        super().react(message)
        if message.performative == ACLMessage.INFORM:
            display_message(self.aid.name, f'🎯 Hora recebida: {message.content}')


if __name__ == '__main__':
    if len(argv) < 2:
        print("Uso: python agent_example_3_workaround.py <porta_base>")
        print("Exemplo: python agent_example_3_workaround.py 20000")
        exit(1)

    agents = list()
    ams_config = {'name': 'localhost', 'port': 8000}
    
    base_port = int(argv[1])
    
    # Cria os AIDs
    time_aid = AID(name=f'agent_time_{base_port}@localhost:{base_port}')
    clock_aid = AID(name=f'agent_clock_{base_port+1}@localhost:{base_port+1}')
    
    # Cria os agentes
    time_agent = TimeAgent(time_aid)
    clock_agent = ClockAgent(clock_aid, time_aid)
    
    # Configura AMS (isso cria o agentInstance)
    time_agent.update_ams(ams_config)
    clock_agent.update_ams(ams_config)
    
    agents.append(time_agent)
    agents.append(clock_agent)
    
    display_message('Sistema', f'🚀 Iniciando {len(agents)} agentes (modo workaround corrigido)')
    start_loop(agents)