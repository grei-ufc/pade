#!/usr/bin/env python3

"""PADE + IEC 61850 integration example for Python 3.12."""

from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID
from pade.behaviours.protocols import FipaRequestProtocol, TimedBehaviour
from pade.misc.data_logger import get_shared_session_id, logger

from sys import argv
import sys

try:
    import pyiec61850 as iec61850
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Missing optional dependency 'pyiec61850'. "
        "Install it in the active environment before running the IEC 61850 example."
    ) from exc


DEFAULT_BASE_PORT = 20000
REQUESTER_OFFSET = 10000
PORT_STRIDE = 500

def testClient(agent_name):
    """Connect to the IEC 61850 server, read the sensor and write a setpoint."""
    tcpPort = 8102
    con = iec61850.IedConnection_create()
    error = iec61850.IedConnection_connect(con, "localhost", tcpPort)

    if error == iec61850.IED_ERROR_OK:
        display_message(agent_name, "Connected to the IEC 61850 IED server.")

        # Read the current sensor value.
        theVal_SV = "testmodelSENSORS/TTMP1.TmpSv.instMag.f"
        theValType_MX = iec61850.IEC61850_FC_MX

        temperatureValue = iec61850.IedConnection_readFloatValue(con, theVal_SV, theValType_MX)
        display_message(agent_name, f"Initial sensor reading: {temperatureValue[0]}")

        # Write a control setpoint.
        theVal_SP = "testmodelSENSORS/TTMP1.TmpSp.setMag.f"
        theValType_SP = iec61850.IEC61850_FC_SP

        newValue = temperatureValue[0] + 10.0
        display_message(agent_name, f"Sending new setpoint command: {newValue}")

        err = iec61850.IedConnection_writeFloatValue(con, theVal_SP, theValType_SP, newValue)

        if err == 0:
            temperatureSetpoint = iec61850.IedConnection_readFloatValue(con, theVal_SP, theValType_SP)
            display_message(agent_name, f"Setpoint updated successfully to: {temperatureSetpoint[0]}")
        else:
            display_message(agent_name, f"Write operation failed with IEC 61850 error code: {err}")

        iec61850.IedConnection_close(con)
    else:
        display_message(agent_name, "Failed to connect to the IEC 61850 IED server.")

    iec61850.IedConnection_destroy(con)


class CompRequest(FipaRequestProtocol):
    def __init__(self, agent):
        super().__init__(agent=agent, message=None, is_initiator=False)

    def handle_request(self, message):
        super().handle_request(message)
        display_message(self.agent.aid.localname, "Control order received. Accessing the IED...")
        testClient(self.agent.aid.localname)

        reply = message.create_reply()
        reply.set_performative(ACLMessage.INFORM)
        reply.set_content("IEC 61850 operation completed")
        self.agent.send(reply)


class CompRequest2(FipaRequestProtocol):
    def __init__(self, agent, message):
        super().__init__(agent=agent, message=message, is_initiator=True)

    def handle_inform(self, message):
        display_message(self.agent.aid.localname, f"Execution report: {message.content}")


class ComportTemporal(TimedBehaviour):
    def __init__(self, agent, time, message):
        super().__init__(agent, time)
        self.message = message

    def on_time(self):
        super().on_time()
        display_message(self.agent.aid.localname, "Timed trigger fired. Sending IEC 61850 request.")
        self.agent.send(self.message)


class IEC61850Agent(Agent):
    def __init__(self, aid):
        super().__init__(aid=aid, debug=False)

    def on_start(self):
        super().on_start()
        self.behaviours.append(CompRequest(self))


class RequestAgent(Agent):
    def __init__(self, aid, target_agent_name):
        super().__init__(aid=aid, debug=False)

        message = ACLMessage(ACLMessage.REQUEST)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        message.add_receiver(AID(name=target_agent_name))
        message.set_content("execute_operation")

        self.comport_request = CompRequest2(self, message)
        self.comport_temp = ComportTemporal(self, 10.0, message)

    def on_start(self):
        super().on_start()
        self.behaviours.append(self.comport_request)
        self.behaviours.append(self.comport_temp)


def _validate_base_port(base_port):
    """Ensure request agent ports remain valid for this legacy-style mapping."""
    if base_port < REQUESTER_OFFSET:
        raise SystemExit(
            f"This example requires a base port >= {REQUESTER_OFFSET}. "
            f"Use for example: pade start-runtime --port {DEFAULT_BASE_PORT} "
            "agent_example_iec_61850_1_updated.py"
        )


if __name__ == "__main__":
    ams_config = {'name': 'localhost', 'port': 8000}
    session_id = get_shared_session_id()
    logger.log_session(session_id=session_id, name="IEC61850_Integration", state="Started")

    base_port = int(argv[1]) if len(argv) > 1 else DEFAULT_BASE_PORT
    _validate_base_port(base_port)

    agents_per_process = 2
    c = 0
    agents = list()

    for i in range(agents_per_process):
        port = base_port + c
        iec_agent_name = f'iec61850_agent_{port}@localhost:{port}'
        iec_agent = IEC61850Agent(AID(name=iec_agent_name))
        iec_agent.update_ams(ams_config)
        agents.append(iec_agent)

        requester_port = port - REQUESTER_OFFSET
        req_agent_name = f'request_agent_{requester_port}@localhost:{requester_port}'
        req_agent = RequestAgent(AID(name=req_agent_name), iec_agent_name)
        req_agent.update_ams(ams_config)
        agents.append(req_agent)

        c += PORT_STRIDE

    display_message('System', "Starting multi-agent IEC 61850 integration...")
    start_loop(agents)
