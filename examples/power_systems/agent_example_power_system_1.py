
from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID
from pade.behaviours.protocols import FipaRequestProtocol
from pade.behaviours.protocols import TimedBehaviour

import numpy as np
from mygrid.power_flow.backward_forward_sweep_3p import calc_power_flow
from ieee_13_bus_system import grid_elements, Load_Node675

import random
from sys import argv


class CompRequest(FipaRequestProtocol):
    """FIPA Request Behaviour of the Time agent.
    """
    def __init__(self, agent):
        super(CompRequest, self).__init__(agent=agent,
                                          message=None,
                                          is_initiator=False)

    def handle_request(self, message):
        super(CompRequest, self).handle_request(message)
        display_message(self.agent.aid.localname, 'request message received')
        
        #power flow calculation
        pp = np.array([[485+1j*190, 68+1j*60, 290+1j*212]]) * 1e3 * random.uniform(0, 3)
        pp.shape = (3, 1)
        Load_Node675.pp = pp
        calc_power_flow(grid_elements.dist_grids['F0'])

        reply = message.create_reply()
        reply.set_performative(ACLMessage.INFORM)
        reply.set_content(Load_Node675.vp)
        self.agent.send(reply)


class CompRequest2(FipaRequestProtocol):
    """FIPA Request Behaviour of the Clock agent.
    """
    def __init__(self, agent, message):
        super(CompRequest2, self).__init__(agent=agent,
                                           message=message,
                                           is_initiator=True)

    def handle_inform(self, message):
        display_message(self.agent.aid.localname, message.content)


class ComportTemporal(TimedBehaviour):
    """Timed Behaviour of the Clock agent"""
    def __init__(self, agent, time, message):
        super(ComportTemporal, self).__init__(agent, time)
        self.message = message

    def on_time(self):
        super(ComportTemporal, self).on_time()
        self.agent.send(self.message)


class PowerFlowAgent(Agent):
    """Class that defines the Time agent."""
    def __init__(self, aid):
        super(PowerFlowAgent, self).__init__(aid=aid, debug=False)

        self.comport_request = CompRequest(self)

        self.behaviours.append(self.comport_request)


class RequestVoltageAgent(Agent):
    """Class thet defines the Clock agent."""
    def __init__(self, aid, time_agent_name):
        super(RequestVoltageAgent, self).__init__(aid=aid)

        # message that requests time of Time agent.
        message = ACLMessage(ACLMessage.REQUEST)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        message.add_receiver(AID(name=time_agent_name))
        message.set_content('time')

        self.comport_request = CompRequest2(self, message)
        self.comport_temp = ComportTemporal(self, 2.0, message)

        self.behaviours.append(self.comport_request)
        self.behaviours.append(self.comport_temp)


if __name__ == '__main__':

    agents_per_process = 2
    c = 0
    agents = list()
    for i in range(agents_per_process):
        port = int(argv[1]) + c
        power_flow_agent_name = 'power_flow_agent_{}@localhost:{}'.format(port, port)
        power_flow_agent = PowerFlowAgent(AID(name=power_flow_agent_name))
        agents.append(power_flow_agent)
        
        request_voltage_agent_name = 'request_voltage_agent_{}@localhost:{}'.format(port - 10000, port - 10000)
        request_voltage_agent = RequestVoltageAgent(AID(name=request_voltage_agent_name), power_flow_agent_name)
        agents.append(request_voltage_agent)

        c += 500

    start_loop(agents)
