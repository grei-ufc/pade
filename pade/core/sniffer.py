"""Framework for Intelligent Agents Development - PADE

The MIT License (MIT)

Copyright (c) 2019 Lucas S Melo

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

from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.misc.utility import display_message, start_loop
from pade.misc.data_logger import get_shared_session_id, logger
from twisted.internet import reactor

from pickle import loads, dumps
import xml.etree.ElementTree as ET
import random
import sys
from datetime import datetime


class Sniffer(Agent):
    """This is the class that implements the Sniffer agent."""

    def __init__(self, host='localhost', port=8001, debug=False):
        self.sniffer_aid = AID('sniffer@' + str(host) + ':' + str(port))
        super(Sniffer, self).__init__(self.sniffer_aid, debug=debug)
        self.sniffer = {'name': str(host), 'port': str(port)}      
        self.host = host
        self.port = port
        self.session_id = get_shared_session_id()
        self.messages_buffer = dict()
        self.buffer_control = True
        self.agent_ids = dict()  # Maps agent names to IDs (in memory)
        self.next_agent_id = 1
        
        # Sniffer initialization log
        logger.log_event(
            event_type="sniffer_initialized",
            data={
                "host": host,
                "port": port,
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
            }
        )

    def _get_or_create_agent_id(self, agent_name):
        """Gets or creates an ID for an agent (in memory)."""
        if agent_name not in self.agent_ids:
            self.agent_ids[agent_name] = self.next_agent_id
            self.next_agent_id += 1
            
            # Log of newly detected agent
            logger.log_event(
                event_type="agent_detected_by_sniffer",
                agent_id=agent_name,
                data={"assigned_id": self.agent_ids[agent_name]}
            )
        
        return self.agent_ids[agent_name]

    def handle_store_messages(self):
        """Processes and stores buffered messages in CSV."""
        for sender, messages in self.messages_buffer.items():
            self._get_or_create_agent_id(sender)
            
            for message in messages:
                # Store canonical agent names so messages.csv stays stable and queryable.
                receivers = ';'.join(
                    [getattr(receiver, 'name', str(receiver)) for receiver in message.receivers]
                )
                
                # Processes the content
                content = message.content
                if isinstance(content, ET.Element):
                    content = ET.tostring(content).decode('utf-8', errors='ignore')
                elif not isinstance(content, str):
                    content = str(content)
                
                # Log the message in CSV
                logger.log_message(
                    message_id=message.messageID if hasattr(message, 'messageID') else f"msg_{datetime.now().timestamp()}",
                    conversation_id=message.conversation_id if hasattr(message, 'conversation_id') else "",
                    agent_id=sender,
                    performative=message.performative if hasattr(message, 'performative') else "",
                    protocol=message.protocol if hasattr(message, 'protocol') else "",
                    sender=message.sender.name if hasattr(message.sender, 'name') else str(message.sender),
                    receivers=receivers,
                    content=content[:500],  # Limits size for CSV
                    ontology=message.ontology if hasattr(message, 'ontology') else "",
                    language=message.language if hasattr(message, 'language') else ""
                )
                
                # Event log (optional, for tracking)
                logger.log_event(
                    event_type="message_stored",
                    agent_id=sender,
                    data={
                        "message_id": message.messageID if hasattr(message, 'messageID') else "unknown",
                        "performative": message.performative if hasattr(message, 'performative') else "",
                        "conversation_id": message.conversation_id if hasattr(message, 'conversation_id') else ""
                    }
                )
                
                if self.debug:
                    display_message(self.aid.name, f'Message from {sender} stored in CSV')

        # Clears the buffer after processing
        self.messages_buffer = dict()
        self.buffer_control = True

    def react(self, message):
        """Processes messages received by the Sniffer."""
        super(Sniffer, self).react(message)
        
        # Ignores messages from AMS
        if 'ams' not in message.sender.name:
            try:
                content = loads(message.content)
                if content['ref'] == 'MESSAGE':
                    _message = content['message']
                    
                    # Adds to buffer
                    sender_name = message.sender.name
                    if sender_name not in self.messages_buffer:
                        self.messages_buffer[sender_name] = [_message]
                    else:
                        self.messages_buffer[sender_name].append(_message)
                    
                    # Schedules buffer processing if necessary
                    if self.buffer_control:
                        # Processes after a random time to avoid overload
                        delay = random.uniform(2.0, 5.0)
                        reactor.callLater(delay, self.handle_store_messages)
                        self.buffer_control = False
                        
                        # Log of scheduled buffer
                        if self.debug:
                            display_message(self.aid.name, f'Buffer processing scheduled in {delay:.2f}s')
            
            except Exception as e:
                # Error log in message processing
                logger.log_event(
                    event_type="sniffer_message_error",
                    data={
                        "error": str(e),
                        "sender": message.sender.name if hasattr(message.sender, 'name') else str(message.sender),
                        "content_preview": str(message.content)[:100]
                    }
                )
                
                if self.debug:
                    display_message(self.aid.name, f'Error processing message: {e}')


def start_sniffer(port=8001, debug=False):
    """Auxiliary function to start the Sniffer."""
    sniffer = Sniffer(port=port, debug=debug)
    
    # Sniffer start log
    logger.log_event(
        event_type="sniffer_started",
        data={
            "port": port,
            "debug": debug,
            "timestamp": datetime.now().isoformat(),
            "session_id": sniffer.session_id,
        }
    )
    
    return sniffer


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python sniffer.py <port>")
        print("Example: python sniffer.py 8001")
        sys.exit(1)
    
    port = int(sys.argv[1])
    debug = len(sys.argv) > 2 and sys.argv[2].lower() == 'debug'
    
    display_message('Sniffer', f'Starting Sniffer on port {port}...')
    
    sniffer = Sniffer(port=port, debug=debug)
    
    # CLI start log
    logger.log_event(
        event_type="sniffer_cli_started",
        data={
            "port": port,
            "debug": debug,
            "command": " ".join(sys.argv),
            "session_id": sniffer.session_id,
        }
    )
    
    start_loop([sniffer])
