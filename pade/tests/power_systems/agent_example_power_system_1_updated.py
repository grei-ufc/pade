#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PADE + IEEE 13-Bus System integration
Migrated to Python 3.12.11 - GREI/UFC project
"""

from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID
from pade.behaviours.protocols import FipaRequestProtocol, TimedBehaviour
from pade.misc.data_logger import get_shared_session_id, logger

import json
import numpy as np
from sys import argv

# Power system dependencies
from mygrid.power_flow.backward_forward_sweep_3p import calc_power_flow
from ieee_13_bus_system import grid_elements, Load_Node675
import random

# --- BEHAVIOURS ---

class CompRequest(FipaRequestProtocol):
    """Receive the request, run the power flow and return the voltage at Node 675."""
    def __init__(self, agent):
        super().__init__(agent=agent, message=None, is_initiator=False)

    def handle_request(self, message):
        super().handle_request(message)
        display_message(self.agent.aid.localname, 'Request received. Starting the power flow calculation...')
        
        try:
            # 1. Randomly change the load to simulate system variability.
            pp = np.array([[485+1j*190, 68+1j*60, 290+1j*212]]) * 1e3 * random.uniform(0, 3)
            pp.shape = (3, 1)
            Load_Node675.pp = pp
            
            # 2. Execute the backward-forward sweep algorithm.
            calc_power_flow(grid_elements.dist_grids['F0'])

            # 3. Serialize the voltage profile as JSON so the logs remain readable.
            voltage_payload = serialize_voltage_profile(Load_Node675.vp)

            reply = message.create_reply()
            reply.set_performative(ACLMessage.INFORM)
            reply.set_ontology('power_flow_voltage')
            reply.set_language('json')
            reply.set_content(json.dumps(voltage_payload))
            self.agent.send(reply)
            
        except Exception as e:
            display_message(self.agent.aid.localname, f"Error during power flow calculation: {e}")

class CompRequest2(FipaRequestProtocol):
    """Supervisory behaviour that receives the calculated voltages."""
    def __init__(self, agent, message):
        super().__init__(agent=agent, message=message, is_initiator=True)

    def handle_inform(self, message):
        try:
            vp_array, formatted_output = parse_voltage_payload(message.content)
            display_message(self.agent.aid.localname, f"Updated voltage at Node 675:\n{formatted_output}")
        except Exception as e:
            display_message(self.agent.aid.localname, f"Failed to extract data: {e}")

class TimedTriggerBehaviour(TimedBehaviour):
    """Timed trigger that requests a new calculation every 3 seconds."""
    def __init__(self, agent, time, message):
        super().__init__(agent, time)
        self.message = message

    def on_time(self):
        super().on_time()
        display_message(self.agent.aid.localname, "Timed trigger fired. Requesting a new power flow reading.")
        self.agent.send(self.message)


def serialize_voltage_profile(voltage_array: np.ndarray) -> dict:
    """Build a JSON-friendly representation of the three-phase voltage profile."""
    vector = np.asarray(voltage_array, dtype=complex).reshape(3,)
    phases = []
    for phase_name, value in zip(('A', 'B', 'C'), vector):
        phases.append({
            'phase': phase_name,
            'real': round(float(value.real), 6),
            'imag': round(float(value.imag), 6),
            'magnitude': round(float(np.abs(value)), 6),
            'angle_deg': round(float(np.degrees(np.angle(value))), 6),
        })
    return {
        'node': '675',
        'unit': 'V',
        'phases': phases,
    }


def parse_voltage_payload(content: str) -> tuple[np.ndarray, str]:
    """Decode the INFORM payload and return both the array and a readable summary."""
    payload = json.loads(content) if isinstance(content, str) else content
    vector = np.array(
        [complex(phase['real'], phase['imag']) for phase in payload['phases']],
        dtype=complex,
    ).reshape(3, 1)

    lines = [f"Node {payload['node']} ({payload.get('unit', 'V')}):"]
    for phase in payload['phases']:
        lines.append(
            "  Phase {phase}: {magnitude:.2f} angle {angle_deg:.2f} deg "
            "({real:.2f} {imag_sign} j{imag_abs:.2f})".format(
                phase=phase['phase'],
                magnitude=phase['magnitude'],
                angle_deg=phase['angle_deg'],
                real=phase['real'],
                imag_sign='+' if phase['imag'] >= 0 else '-',
                imag_abs=abs(phase['imag']),
            )
        )
    return vector, "\n".join(lines)

# --- AGENTS ---

class PowerFlowAgent(Agent):
    """Agent responsible for the power system calculations."""
    def __init__(self, aid):
        super().__init__(aid=aid, debug=False)

    def on_start(self):
        super().on_start()
        self.behaviours.append(CompRequest(self))

class RequestVoltageAgent(Agent):
    """Supervisory agent for the distribution network."""
    def __init__(self, aid, target_agent_name):
        super().__init__(aid=aid)

        message = ACLMessage(ACLMessage.REQUEST)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        message.add_receiver(AID(name=target_agent_name))
        message.set_content('Request_Node_675_Reading')

        self.request_behaviour = CompRequest2(self, message)
        # The timer is set to 3.0s to reduce CPU pressure on slower machines.
        self.timer_behaviour = TimedTriggerBehaviour(self, 3.0, message)

    def on_start(self):
        super().on_start()
        self.behaviours.append(self.request_behaviour)
        self.behaviours.append(self.timer_behaviour)

# --- EXECUTION ---

if __name__ == '__main__':
    ams_config = {'name': 'localhost', 'port': 8000}
    session_id = get_shared_session_id()
    logger.log_session(session_id=session_id, name="PowerFlow_IEEE13", state="Started")

    base_port = int(argv[1]) if len(argv) > 1 else 20000
    if base_port < 10000:
        raise SystemExit(
            "The power_systems example uses paired requester ports based on base_port - 10000. "
            "Please run it with a base port of at least 10000, for example: "
            "'pade start-runtime --port 20000 agent_example_power_system_1_updated.py'."
        )
    agents_per_process = 2
    c = 0
    agents = list()
    
    for i in range(agents_per_process):
        port = base_port + c
        
        pf_agent_name = f'power_flow_agent_{port}@localhost:{port}'
        pf_agent = PowerFlowAgent(AID(name=pf_agent_name))
        pf_agent.update_ams(ams_config)
        agents.append(pf_agent)
        
        req_agent_name = f'request_voltage_agent_{port - 10000}@localhost:{port - 10000}'
        req_agent = RequestVoltageAgent(AID(name=req_agent_name), pf_agent_name)
        req_agent.update_ams(ams_config)
        agents.append(req_agent)

        c += 500

    display_message('System', "Starting multi-agent power flow integration (IEEE-13)...")
    start_loop(agents)
