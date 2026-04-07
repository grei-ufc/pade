from sys import argv

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.core.agent import Agent
from pade.misc.data_logger import get_shared_session_id, logger
from pade.misc.utility import display_message, start_loop


class HelloReceiverAgent(Agent):
    def __init__(self, aid):
        super().__init__(aid=aid, debug=False)

    def on_start(self):
        super().on_start()
        display_message(self.aid.localname, 'Hello World! Receiver online.')

    def react(self, message):
        super().react(message)

        if message.ontology != 'hello_world_ontology':
            return

        display_message(
            self.aid.localname,
            f'Received message: {message.content}',
        )


class HelloSenderAgent(Agent):
    def __init__(self, aid, receiver_aid):
        super().__init__(aid=aid, debug=False)
        self.receiver_aid = receiver_aid

    def on_start(self):
        super().on_start()
        display_message(self.aid.localname, 'Hello World! Sender online.')

        # Wait a moment so both agents are visible in the AMS before sending.
        self.call_later(2.0, self.send_hello_world_message)

    def send_hello_world_message(self):
        display_message(
            self.aid.localname,
            f'Sending Hello World message to {self.receiver_aid.localname}',
        )

        message = ACLMessage(ACLMessage.INFORM)
        message.add_receiver(self.receiver_aid)
        message.set_ontology('hello_world_ontology')
        message.set_content('Hello World Message!')
        self.send(message)


if __name__ == '__main__':
    ams_config = {'name': 'localhost', 'port': 8000}
    session_id = get_shared_session_id()

    logger.log_session(
        session_id=session_id,
        name=f'HelloWorld_{session_id}',
        state='Started',
    )

    base_port = int(argv[1]) if len(argv) > 1 else 20000

    receiver_port = base_port
    sender_port = base_port + 1000

    receiver_aid = AID(name=f'hello_receiver_{receiver_port}@localhost:{receiver_port}')
    sender_aid = AID(name=f'hello_sender_{sender_port}@localhost:{sender_port}')

    receiver_agent = HelloReceiverAgent(receiver_aid)
    sender_agent = HelloSenderAgent(sender_aid, receiver_aid)

    for agent in (receiver_agent, sender_agent):
        agent.update_ams(ams_config)

    start_loop([receiver_agent, sender_agent])
