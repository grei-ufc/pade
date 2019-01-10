import json

class MosaikCon(object):

    def __init__(self, mosaik_models, agent, time_step=1):
        self.models = mosaik_models
        self.agent = agent
        self.sim_id = None
        self.msg_id = None
        self.time = 0
        self.inputs = dict()
        self.outputs = dict()
        self.data = dict()
        self.time_step = time_step
        self.progress = None
        self.async_requests = list()

    def _process_message(self, message):
        header = int.from_bytes(message[:4], byteorder='big')
        payload = json.loads(message[4:])
        type_ = payload[0]
        self.msg_id = int(payload[1])
        msg_id_respose = int(payload[1])
        content_ = payload[2]
        
        if type(content_) is not list:
            if self.async_requests != []:
                async_request = self.async_requests.pop()
                if async_request == 'get_progress':
                    self.handle_get_progress(content_)
                elif async_request == 'get_data':
                    self.handle_get_data(content_)
                elif async_request == 'set_data':
                    self.handle_set_data()
            return None
        else:
            function = content_[0]
            func_args = content_[1]
            func_kargs = content_[2]
            if function == 'init':
                self.sim_id = func_args[0]
                params = func_kargs
                message = self.__create_message(1, msg_id_respose, self.init(self.sim_id, *params))
            elif function == 'create':
                num = func_args[0]
                model = func_args[1]
                params = func_kargs
                message = self.__create_message(1, msg_id_respose, self.create(num, model, **params))

            elif function == 'setup_done':
                self.setup_done()
                message = self.__create_message(1, msg_id_respose, None)

            elif function == 'step':
                self.time = func_args[0]
                self.inputs = func_args[1]
                message = self.__create_message(1, msg_id_respose, self.step(self.time, self.inputs))

            elif function == 'get_data':
                self.outputs = func_args[0]
                message = self.__create_message(1, msg_id_respose, self.get_data(self.outputs))

            elif function == 'stop':
                self.stop()
                message = self.__create_message(1, msg_id_respose, None)

        return message

    def init(self, *params):
        return self.models

    def create(self, num, model, **kargs):
        entities_info = list()
        for i in range(num):
            entities_info.append(
                {'eid': self.sim_id + '.' + str(i), 'type': model})
        return entities_info

    def setup_done(self):
        pass

    def step(self, time, inputs):
        return time + self.time_step

    def get_data(self, outputs):
        response = dict()
        for model, list_values in outputs.items():
            response[model] = dict()
            for value in list_values:
                response[model][value] = None
        return response

    def stop(self):
        pass

    def get_progress(self):
        m = ['get_progress', [], {}]
        self.msg_id += 1
        message = self.__create_message(0, self.msg_id, m)
        self.agent.mosaik_connection.transport.write(message)
        self.async_requests.append('get_progress')

    def handle_get_progress(self, progress):
        pass

    def get_data_async(self, data):
        m = ['get_data', [data], {}]
        self.msg_id += 1
        message = self.__create_message(0, self.msg_id, m)
        self.agent.mosaik_connection.transport.write(message)
        self.async_requests.append('get_data')

    def handle_get_data(self, data):
        pass

    def set_data_async(self, data):
        m = ['set_data', [data], {}]
        self.msg_id += 1
        message = self.__create_message(0, self.msg_id, m)
        self.agent.mosaik_connection.transport.write(message)
        self.async_requests.append('set_data')

    def handle_set_data(self):
        pass

    def __create_message(self, msg_type, id_, content):
        a = json.dumps([msg_type, id_, content])
        b = bytes(a, 'utf-8')
        c = int.to_bytes(len(b), 4, byteorder='big')
        d = c + b
        return d
