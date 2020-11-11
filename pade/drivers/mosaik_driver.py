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
        self.deferred = None
        self.msg_id_step = None
        self.step_size = 1000

    def _process_message(self, message, mosaik_msg_id=None):
        header = int.from_bytes(message[:4], byteorder='big')
        payload = json.loads(message[4:])
        type_ = payload[0]
        self.msg_id = int(payload[1])
        msg_id_respose = int(payload[1])
        content_ = payload[2]

        if type_ == 2:
            print(content_)
            raise Exception('Mosaik error message!')

        try:
            function = content_[0]
            func_args = content_[1]
            func_kargs = content_[2]    
        except Exception as e:
            raise 

        if function == 'init':
            self.sim_id = func_args[0]
            params = func_kargs
            message = self._create_message(1, msg_id_respose, self.init(self.sim_id, **params))
        elif function == 'create':
            num = func_args[0]
            model = func_args[1]
            params = func_kargs
            message = self._create_message(1, msg_id_respose, self.create(num, model, **params))

        elif function == 'setup_done':
            self.setup_done()
            message = self._create_message(1, msg_id_respose, None)

        elif function == 'step':
            self.time = func_args[0]
            self.inputs = func_args[1]
            self.msg_id_step = msg_id_respose
            return_value = self.step(self.time, self.inputs)

            '''
                Aqui três casos são possíveis:
                1. step não tem yield: por isso é necessário verificar antes
                essa condição. utilizando inspect.isgenerator()

                2. step tem yield mas não o utiliza, por que ele pode estar 
                dentro de uma estrutura if. Nesse caso deve ser verificado
                o valor de retorno quando o next é chamado. Se o valor
                retornado for um inteiro, significa que não há chamada
                assícrona neste step;

                3. step tem yield e o utiliza. Neste caso existe yield
                dentro do método e ele é utilizado para fazer uma chamada
                assíncrona ao Mosaik. Dessa forma, um valor None é retornado
                e o gerador deve aguardar a resposta da chamada assíncrona
                para que possa continuar sua execução. O método, _process_message,
                ele próprio devolve o valor do ID da mensagem atual para o método
                dataReceived do Pade, pausando o seu comportamento e aguardando
                a chegada da resposta da chamada assíncrona.
            '''

            if inspect.isgenerator(return_value):
                # ativa o primeiro yield ou return
                try:
                    r_ = next(return_value)
                except StopIteration as e:
                    r_ = e.value

                # se retornar None, o yield foi ativado
                # se não o retorno é um inteiro
                if r_ is None:
                    # ========================================
                    # EXISTE CHAMADA ASSÍNCRONA NO STEP ATUAL
                    # ========================================

                    async_message = yield self.msg_id
                    # =============================
                    # RETORNO DA CHAMADA ASSÍNCRONA
                    # =============================
                    try:
                        if self.async_requests != []:
                            async_request = self.async_requests.pop()

                            if async_request == 'get_progress':
                                progress = self.handle_get_progress(async_message)
                                return_value = return_value.send(progress)
                            elif async_request == 'get_data':
                                data = self.handle_get_data(async_message)
                                return_value = return_value.send(data)
                            elif async_request == 'set_data':
                                return_value = next(return_value)
                    except StopIteration as e:
                        return_value = e.value
                else:
                    # ========================================
                    # NÃO EXISTE CHAMADA ASSÍNCRONA NO STEP ATUAL
                    # ========================================
                    return_value = r_

            # verificar se um valor inteiro
            # está sendo retornado do método step. Se o valor
            # retornado for None, significa que o agente está
            # aguardando por uma valor externo para concluir
            # seu comportamento step.
            if return_value:
                # ====================
                # STEP ATUAL CONCLUÍDO
                # ====================
                message = self._create_message(1, msg_id_respose, return_value)
            else:
                # =========================================
                # STEP ATUAL AGUARDANDO RESPOSTA ASSÍNCRONA
                # =========================================
                return

        elif function == 'get_data':
            self.outputs = func_args[0]
            message = self._create_message(1, msg_id_respose, self.get_data(self.outputs))
        elif function == 'stop':
            self.stop()
            message = self._create_message(1, msg_id_respose, None)

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

    def step_done(self):
        message = self._create_message(1, self.msg_id_step, self.time + self.step_size)
        self.agent.mosaik_connection.transport.write(message)
        self.agent.mosaik_connection.message = None
        self.agent.mosaik_connection.mosaik_msg_id = None
        self.agent.mosaik_connection.await_gen = None

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
        message = self._create_message(0, self.msg_id, m)
        self.agent.mosaik_connection.message = None
        self.agent.mosaik_connection.transport.write(message)
        self.async_requests.append('get_progress')

    def handle_get_progress(self, message):
        header = int.from_bytes(message[:4], byteorder='big')
        payload = json.loads(message[4:])
        type_ = payload[0]
        self.msg_id = int(payload[1])
        msg_id_respose = int(payload[1])
        content_ = payload[2]
        return content_

    def get_data_async(self, data):
        m = ['get_data', [data], {}]
        self.msg_id += 1
        message = self._create_message(0, self.msg_id, m)
        self.agent.mosaik_connection.message = None
        self.agent.mosaik_connection.transport.write(message)
        self.async_requests.append('get_data')

    def handle_get_data(self, message):
        header = int.from_bytes(message[:4], byteorder='big')
        payload = json.loads(message[4:])
        type_ = payload[0]
        self.msg_id = int(payload[1])
        msg_id_respose = int(payload[1])
        content_ = payload[2]
        return content_

    def set_data_async(self, data):
        m = ['set_data', [data], {}]
        self.msg_id += 1
        message = self._create_message(0, self.msg_id, m)
        self.agent.mosaik_connection.message = None
        self.agent.mosaik_connection.transport.write(message)
        self.async_requests.append('set_data')

    def handle_set_data(self):
        pass

    def _create_message(self, msg_type, id_, content):
        a = json.dumps([msg_type, id_, content])
        b = bytes(a, 'utf-8')
        c = int.to_bytes(len(b), 4, byteorder='big')
        d = c + b
        return d
