from pade.core.agent import Agent_
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID
from pade.behaviours.protocols import TimedBehaviour, FipaRequestProtocol, FipaSubscribeProtocol
from pade.misc.utility import display_message
from pade.acl.filters import Filter
from pade.web.flask_server import db, AgentModel, Message, Session

from pickle import dumps, loads
from datetime import datetime

from terminaltables import AsciiTable

# Comportamento que envia as mensagens de verificacao da conexao

class ComportSendConnMessages(TimedBehaviour):
    def __init__(self, agent, message, time):
        super(ComportSendConnMessages, self).__init__(agent, time)
        self.message = message

    def on_time(self):
        super(ComportSendConnMessages, self).on_time()
        self.agent.add_all(self.message)
        self.agent.send(self.message)
        display_message(self.agent.aid.name, 'Connection...')

# Comportamento que verifica os tempos de resposta dos
# agentes e decide desconecta-los ou nao

class ComportVerifyConnTimed(TimedBehaviour):
    def __init__(self, agent, time):
        super(ComportVerifyConnTimed, self).__init__(agent, time)

    def on_time(self):
        super(ComportVerifyConnTimed, self).on_time()
        desconnect_agents = list()
        table = list([['agente', 'delta']])
        for agent_name, date in self.agent.agents_conn_time.items():
            now = datetime.now()
            delta = now - date
            table.append([agent_name, str(delta.total_seconds())])
            if delta.total_seconds() > 10.0:
                desconnect_agents.append(agent_name)
                self.agent.agentInstance.table.pop(agent_name)

        for agent_name in desconnect_agents:
            self.agent.agents_conn_time.pop(agent_name)

        display_message(self.agent.aid.name, 'verifing connections...')
        table = AsciiTable(table)
        print(table.table)


class CompConnectionVerify(FipaRequestProtocol):
    """Comportamento FIPA Request
    do agente Relogio"""
    def __init__(self, agent, message):
        super(CompConnectionVerify, self).__init__(agent=agent,
                                           message=message,
                                           is_initiator=True)
        

    def handle_inform(self, message):
        display_message(self.agent.aid.localname, message.content)
        date = datetime.now()
        self.agent.agents_conn_time[message.sender.name] = date


class PublisherBehaviour(FipaSubscribeProtocol):
    """Comportamento FipaSubscribe tipo Publisher que implementa
       uma comunicacao publisher-subscriber, onde o publisher eh o
       agente AMS e os subscribers sao os agentes da plataforma.
       Neste comportamento dois procedimentos sao implementados:
         - O primeiro dos procedimentos eh o de identificacao em que
           a disponibilidade eh verificada no banco de dados e se dispo-
           nivel, armazenada.
         - O segundo procedimento eh a atualizacao das tabelas distribuidas
           que contem os enderecos dos agentes presentes na plataforma, sempre
           que um agente entra ou sai da rede."""

    def __init__(self, agent):
        super(PublisherBehaviour, self).__init__(agent,
                                                 message=None,
                                                 is_initiator=False)

    def handle_subscribe(self, message):

        sender = message.sender

        if sender in self.agent.agentInstance.table.values():
            display_message(self.agent.aid.name,
                            'Falha na Identificacao do agente ' + sender.name)

            # prepara mensagem de resposta
            reply = message.create_reply()
            reply.set_content(
                'Ja existe um agente com este identificador. Por favor, escolha outro.')
            # envia mensagem
            self.agent.send(reply)
        else:
            # registra o agente no banco de dados

            a = AgentModel(name=sender.localname,
                      session_id=self.agent.session.id,
                      date=datetime.now(),
                      state='Ativo')
            db.session.add(a)
            db.session.commit()

            # cadastra o agente na tabela de agentes
            self.agent.agentInstance.table[sender.name] = sender
            # registra no agente como assinante no protocolo
            self.register(message.sender)
            # registra o agente na tabela de tempo
            self.agent.agents_conn_time[message.sender.name] = datetime.now()

            display_message(
                self.agent.aid.name, 'Agente ' + sender.name + ' identificado com sucesso')

            # prepara e envia mensagem de resposta ao agente
            reply = message.create_reply()
            reply.set_performative(ACLMessage.AGREE)
            reply.set_content(
                'Agente Identificado com sucesso.')
            self.agent.send(reply)

            # prepara e envia mensagem de atualizacao para
            # todos os agentes cadastrados
            message = ACLMessage(ACLMessage.INFORM)
            message.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)
            message.set_content(dumps(self.agent.agentInstance.table))
            message.set_system_message(is_system_message=True)            
            self.notify(message)

    def handle_cancel(self, message):
        self.deregister(self, message.sender)
        display_message(self.agent.aid.name, message.content)

    def notify(self, message):
        super(PublisherBehaviour, self).notify(message)


class CompVerifyRegister(FipaRequestProtocol):
    def __init__(self, agent):
        """Comportamento FIPA Request para
        verificacao de registro de usuario"""
        super(CompVerifyRegister, self).__init__(agent=agent,
                                                 message=None,
                                                 is_initiator=False)

    def handle_request(self, message):
        super(CompVerifyRegister, self).handle_request(message)
        content = loads(message.content)
        display_message(self.agent.aid.name,
                        'Validando sessao do agente ' + message.sender.name)
        if type(content) == dict:
            if content['ref'] == "REGISTER":
                user_login = content['content']['user_login']
                session_name = content['content']['session_name']

                # procedimento de verificacao de dados da sessao
                # e do usuario da sessao solicitada

                # pesquisa no banco de dados se existe uma sessao com este nome
                session = Session.query.filter_by(name=session_name).first()
                if session is None:
                    reply = message.create_reply()
                    reply.set_performative(ACLMessage.INFORM)
                    reply.set_content(dumps({'ref': 'REGISTER',
                                             'content': False}))
                    self.agent.call_later(1.0, self.agent.send, reply)
                else:
                    # verifica se o usuario esta logado na sessao
                    users = session.users
                    for user in users:
                        if user.username == user_login['username']:
                            if user.verify_password(user_login['password']):
                                validation = True
                                display_message(self.agent.aid.name,
                                                'Sessao validada com sucesso.')
                                break
                            else:
                                validation = False
                                display_message(self.agent.aid.name,
                                                'Sessao nao validada -> Senha incorreta.')
                                break
                    else:
                        display_message(self.agent.aid.name,
                                        'Sessao nap validada-> Usuario nao existe.')
                        validation = False

                    reply = message.create_reply()
                    reply.set_performative(ACLMessage.INFORM)
                    reply.set_content(dumps({'ref': 'REGISTER',
                                             'content': validation}))
                    self.agent.send(reply)

class AMS(Agent_):
    """Esta e a classe que implementa o agente AMS."""

    def __init__(self, host, port, session, main_ams=True, debug=False):
        self.ams_aid = AID('ams@' + str(host) + ':' + str(port))
        super(AMS, self).__init__(self.ams_aid)
        self.host = host
        self.port = port
        self.session = session
        self.main_ams = main_ams

        self.agents_conn_time = dict()
        self.comport_ident = PublisherBehaviour(self)

        # mensagem para verificacao de conexcao
        message = ACLMessage(ACLMessage.REQUEST)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        self.add_all(message)
        message.set_content('CONNECTION')
        message.set_system_message(is_system_message=True)

        self.comport_conn_verify = CompConnectionVerify(self, message)
        self.comport_send_conn_messages = ComportSendConnMessages(self, message, 4.0)
        self.comport_conn_verify_timed = ComportVerifyConnTimed(self, 10.0)
        self.comport_conn_verify_reg = CompVerifyRegister(self)

        self.system_behaviours.append(self.comport_ident)
        self.system_behaviours.append(self.comport_conn_verify)
        self.system_behaviours.append(self.comport_send_conn_messages)
        self.system_behaviours.append(self.comport_conn_verify_timed)
        self.system_behaviours.append(self.comport_conn_verify_reg)
        self.on_start()

    def handle_store_messages(self, message, sender):

        m = Message(sender=message.sender.localname,
                    date=message.datetime,
                    performative=message.performative,
                    protocol=message.protocol,
                    content=message.content,
                    conversation_id=message.conversationID,
                    message_id=message.messageID,
                    ontology=message.ontology,
                    language=message.language)

        receivers = list()
        for receiver in message.receivers:
            receivers.append(receiver.localname)
        m.receivers = receivers

        a = AgentModel.query.filter_by(name=sender.localname).all()[0]
        m.agent_id = a.id

        db.session.add(m)
        db.session.commit()

        display_message(self.aid.name, 'Message stored')

    def react(self, message):
        super(AMS, self).react(message)

        try:
            content = loads(message.content)
            if content['ref'] == 'MESSAGE':
                _message = content['message']
                if _message.sender.localname != 'ams':
                    self.handle_store_messages(_message, message.sender)
        except:
            pass

