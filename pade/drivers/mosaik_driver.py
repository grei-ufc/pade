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

import json
from twisted.internet import defer
import inspect
import types

class MosaikCon(object):

    def __init__(self, mosaik_models, agent, time_step=1):
        self.models = mosaik_models
        self.agent = agent
        self.sim_id = None
        self.msg_id = 0
        self.time_resolution = None
        self.time = 0
        self.inputs = dict()
        self.outputs = dict()
        self.data = dict()
        self.time_step = time_step
        self.progress = None
        self.async_requests = list()
        self.deferred = None
        self.msg_id_step = None
        self.step_size = 1000
        self.meta = mosaik_models

    def _process_message(self, message, mosaik_msg_id=None):
        """Shielded message processor. 
        Ensures the function always behaves as a generator (yield)."""
        
        # 1. Packet Decoding
        payload = json.loads(message[4:])
        type_ = payload[0]
        id_received = int(payload[1])
        content_ = payload[2]

        if type_ == 2:
            print(f"❌ Mosaik Error: {content_}")
            raise Exception('Mosaik error message!')

        # TYPE 1: RESPONSE (The Agent receives data it requested via yield)
        if type_ == 1:
            if self.async_requests:
                async_request = self.async_requests.pop()
                if async_request == 'get_progress':
                    self.handle_get_progress(content_)
                elif async_request == 'get_data':
                    self.handle_get_data(content_)
                elif async_request == 'set_data':
                    self.handle_set_data()
            
            # In Python 3, we use yield None to maintain the generator nature
            # and return to pass the value to the StopIteration that peer.py reads.
            yield None
            return id_received

        # TYPE 0: COMMAND (Mosaik commands the Agent to act)
        else:
            try:
                function = content_[0]
                func_args = content_[1]
                func_kargs = content_[2]    
            except Exception:
                yield b''
                return

            if function == 'init':
                self.sim_id = func_args[0]
                # Mosaik 3 sends time_resolution here
                res = self.init(self.sim_id, **func_kargs)
                yield self._create_message(1, id_received, res)

            elif function == 'create':
                num, model = func_args[0], func_args[1]
                res = self.create(num, model, **func_kargs)
                yield self._create_message(1, id_received, res)

            elif function == 'setup_done':
                self.setup_done()
                yield self._create_message(1, id_received, None)

            elif function == 'step':
                self.time = func_args[0]
                self.inputs = func_args[1]
                # Support for max_advance in Mosaik 3
                self.max_advance = func_args[2] if len(func_args) > 2 else 0
                self.msg_id_step = id_received
                
                r_step = self.step(self.time, self.inputs, self.max_advance)

                # Multiple Yields Management (Fix for 20% deadlock)
                if inspect.isgenerator(r_step):
                    while True:
                        try:
                            val = next(r_step)
                            if val is None:
                                # The agent yielded. We signal the pause ID.
                                yield id_received 
                            else:
                                r_final = val
                                break
                        except StopIteration as e:
                            r_final = e.value
                            break
                else:
                    r_final = r_step
                
                if r_final is not None:
                    yield self._create_message(1, id_received, r_final)

            elif function == 'get_data':
                self.outputs = func_args[0]
                res = self.get_data(self.outputs)
                yield self._create_message(1, id_received, res)
            
            elif function == 'stop':
                self.stop()
                yield self._create_message(1, id_received, None)

    def init(self, sid, **kwargs):
        return self.models

    def create(self, num, model, **kargs):
        entities_info = list()
        for i in range(num):
            entities_info.append({'eid': f"{self.sim_id}.{i}", 'type': model})
        return entities_info

    def setup_done(self):
        pass

    def step(self, time, inputs, max_advance):
        return time + self.time_step

    def step_done(self):
        message = self._create_message(1, self.msg_id_step, self.time + self.step_size)
        self.agent.mosaik_connection.transport.write(message)
        self.agent.mosaik_connection.message = None
        self.agent.mosaik_connection.mosaik_msg_id = None
        self.agent.mosaik_connection.await_gen = None

    def get_data(self, outputs):
        response = dict()
        for model, list_values in outputs.items():
            response[model] = {value: None for value in list_values}
        return response

    def stop(self):
        pass

    def get_progress(self):
        self.msg_id += 1
        m = ['get_progress', [], {}]
        message = self._create_message(0, self.msg_id, m)
        self.agent.mosaik_connection.message = None
        self.agent.mosaik_connection.transport.write(message)
        self.async_requests.append('get_progress')

    def handle_get_progress(self, progress):
        pass

    def get_data_async(self, data):
        self.msg_id += 1
        m = ['get_data', [data], {}]
        message = self._create_message(0, self.msg_id, m)
        self.agent.mosaik_connection.message = None
        self.agent.mosaik_connection.transport.write(message)
        self.async_requests.append('get_data')

    def handle_get_data(self, data):
        pass

    def set_data_async(self, data):
        self.msg_id += 1
        m = ['set_data', [data], {}]
        message = self._create_message(0, self.msg_id, m)
        self.agent.mosaik_connection.message = None
        self.agent.mosaik_connection.transport.write(message)
        self.async_requests.append('set_data')

    def handle_set_data(self):
        pass

    def _create_message(self, msg_type, id_, content):
        a = json.dumps([msg_type, id_, content])
        b = bytes(a, 'utf-8')
        return int.to_bytes(len(b), 4, byteorder='big') + b