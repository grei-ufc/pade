from sys import argv

from pade.acl.aid import AID
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop


class HelloWorldAgent(Agent):
    def __init__(self, aid):
        super().__init__(aid=aid, debug=False)

    def on_start(self):
        super().on_start()
        display_message(self.aid.localname, 'Hello World!')


if __name__ == '__main__':
    ams_config = {'name': 'localhost', 'port': 8000}
    base_port = int(argv[1]) if len(argv) > 1 else 20000

    agent = HelloWorldAgent(
        AID(name=f'hello_agent_{base_port}@localhost:{base_port}')
    )
    agent.update_ams(ams_config)

    start_loop([agent])
