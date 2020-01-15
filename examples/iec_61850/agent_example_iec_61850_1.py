
from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID
from pade.behaviours.protocols import FipaRequestProtocol
from pade.behaviours.protocols import TimedBehaviour

import iec61850

import random
from sys import argv

def testClient():
    tcpPort = 8102
    con = iec61850.IedConnection_create()
    error = iec61850.IedConnection_connect(con, "localhost", tcpPort)
    if (error == iec61850.IED_ERROR_OK):
        # Accessing to SAV values
        theVal = "testmodelSENSORS/TTMP1.TmpSv.instMag.f"
        theValType = iec61850.IEC61850_FC_MX
        temperatureValue = iec61850.IedConnection_readFloatValue(con, theVal, theValType)
        assert(temperatureValue[1]==0)
        newValue= temperatureValue[0]+10
        err = iec61850.IedConnection_writeFloatValue(con, theVal, theValType, newValue)
        assert(err==21)
        # Accessing to ASG values
        theVal = "testmodelSENSORS/TTMP1.TmpSp.setMag.f"
        theValType = iec61850.IEC61850_FC_SP
        temperatureSetpoint = iec61850.IedConnection_readFloatValue(con, theVal, theValType)
        print(temperatureSetpoint)
        assert(temperatureValue[1]==0)
        newValue= temperatureValue[0]+10
        err = iec61850.IedConnection_writeFloatValue(con, theVal, theValType, newValue)
        assert(err==0)
        temperatureSetpoint = iec61850.IedConnection_readFloatValue(con, theVal, theValType)
        print(temperatureSetpoint)
        assert(temperatureSetpoint[0]==newValue)
        iec61850.IedConnection_close(con)
    else:
        print("Connection error")
        sys.exit(-1)
    iec61850.IedConnection_destroy(con)
    print("client ok")

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

        testClient()

        reply = message.create_reply()
        reply.set_performative(ACLMessage.INFORM)
        reply.set_content("OK")
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


class IEC61850Agent(Agent):
    """Class that defines the Time agent."""
    def __init__(self, aid):
        super(IEC61850Agent, self).__init__(aid=aid, debug=False)

        self.comport_request = CompRequest(self)

        self.behaviours.append(self.comport_request)


class RequestAgent(Agent):
    """Class thet defines the Clock agent."""
    def __init__(self, aid, time_agent_name):
        super(RequestAgent, self).__init__(aid=aid)

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
        iec61850_agent_name = 'iec61850_agent_{}@localhost:{}'.format(port, port)
        iec61850_agent = IEC61850Agent(AID(name=iec61850_agent_name))
        agents.append(iec61850_agent)
        
        request_agent_name = 'request_agent_{}@localhost:{}'.format(port - 10000, port - 10000)
        request_agent = RequestAgent(AID(name=request_agent_name), iec61850_agent_name)
        agents.append(request_agent)

        c += 500

    start_loop(agents)
