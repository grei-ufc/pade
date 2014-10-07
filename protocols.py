# -*- encoding: utf-8 -*-

"""
    Módulo de protocolos
    --------------------

    Este modulo implementa os protocolos padronizados pela FIPA:
    1. FipaRequestProtocol
    2. FipaContractNetProtocol
    3. FIPA_Subscribe_Protocol
"""

import twisted
from messages import ACLMessage
from filters import Filter
from time import time


class Behaviour(object):

    """
        Classe Behaviopur
        -----------------

        Classe que declara os metodos essenciais de um comportamento,
        todo comportamento deve herdar esta classe.
    """

    def __init__(self, agent):
        """
            Inicializa a classe Behaviour com uma instancia agent

            Parâmetros
            ----------
            agent : instancia do agente que executara os comportamentos
                    estabelecidos pelo protocolo

        """
        super(Behaviour, self).__init__()
        self.agent = agent
        self.timeout = 1

    def execute(self, message):
        """
            execute
            -------

            Executa o comportamento propriamente dito do protocolo
            para cada tipo de mensagem recebida
        """
        pass

    def timed_behaviour(self):
        """
            timed_behaviour
            ---------------

            Utilizado quando o protocolo implementado possui restrições
            de tempo, como por exemplo utilização de timeout
        """
        pass

    def on_start(self):
        """
            on_start
            --------

            Executado sempre que o protocolo e Inicializado
        """
        self.t1 = int(time())

class TimedBehaviour(Behaviour):
    """
        TimedBehaviour
        --------------
    """
    def __init__(self, agent, time):
        """
            método de inicialização
            -----------------------
        """
        super(TimedBehaviour, self).__init__(agent)
        self.time = time

    def on_start(self):
        """
            on_start
            --------

            Este método sobrescreve o metoso on_start da classe
            Behaviour e implementa configurações adicionais
            à inicialização do comportamento TimedBehaviour
        """
        Behaviour.on_start(self)
        self.timed_behaviour()


    def timed_behaviour(self):
        """
            timed_behaviour
            ---------------

            Este método é implementado sempre que o comportamento a ser 
            implementado necessitar de restrições temporais.
            Neste caso ele faz uso do método callLater do twisted 
            que recebe como parâmetro um método e o atrazo de tempo para
            que este método seja executado

        """
        Behaviour.timed_behaviour(self)

        twisted.internet.reactor.callLater(self.time,
                                           self.on_time)

    def on_time(self):
        """
            execute_on_timeout
            ------------------

            Este método executa o método handle_all_proposes caso nem
            todas as mensagens FIPA_CFP enviadas pelo agente obtenham
            resposta
        """
        twisted.internet.reactor.callLater(self.time,
                                           self.on_time)

class FipaRequestProtocol(Behaviour):

    """
        FipaRequestProtocol
        ---------------------

        Classe que implementa o protocolo FipaRequestProtocol
        herdando a classe Behaviour e implementando seus métodos
    """

    def __init__(self, agent, message=None, is_initiator=True):
        """
            Inicializa a classe que implementa o protocolo
            FipaRequestProtocol

            Parâmetros
            ----------
            agent : instância do agente que executara os comportamentos
                    estebelecidos pelo protocolo
            message : mensagem a ser enviada pelo agente quando o 
                      parâmetro is_initiator for verdadeiro
            is_initiator : parâmetro do tipo booleano que indica se esta 
                          instancia do protocolo agirá como Initiator
                          ou como participante

        """
        super(FipaRequestProtocol, self).__init__(agent)

        self.is_initiator = is_initiator
        self.message = message

        self.filter_protocol = Filter()
        self.filter_protocol.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)

        self.filter_Request = Filter()
        self.filter_Request.set_performative(ACLMessage.REQUEST)

        self.filter_refuse = Filter()
        self.filter_refuse.set_performative(ACLMessage.REFUSE)

        self.filter_Agree = Filter()
        self.filter_Agree.set_performative(ACLMessage.AGREE)

        self.filter_failure = Filter()
        self.filter_failure.set_performative(ACLMessage.FAILURE)

        self.filter_inform = Filter()
        self.filter_inform.set_performative(ACLMessage.INFORM)

    def on_start(self):
        """
            on_start
            --------

            Este método sobrescreve o metoso on_start da classe
            Behaviour e implementa configurações adicionais
            à inicialização do protocolo FipaRequestProtocol
        """

        Behaviour.on_start(self)

        if self.is_initiator and self.message != None:
            self.agent.send(self.message)

    def handle_request(self, message):
        """
            handle_request
            --------------

            Este método deve ser sobrescrito quando na implementação
            do protocolo, sendo executado sempre que o agente receber
            uma mensagem do tipo FIPA_REQUEST

            Parâmetros
            ----------
            message : Mensagem FIPA-ACL
        """
        pass

    def handle_refuse(self, message):
        """
            handle_refuse
            -------------

            Este método deve ser sobrescrito quando na implementação
            do protocolo, sendo executado sempre que o agente receber
            uma mensagem do tipo FIPA_REFUSE

            Parâmetros
            ----------
            message : Mensagem FIPA-ACL
        """
        pass

    def handle_agree(self, message):
        """
            handle_agree
            ------------

            Este método deve ser sobrescrito quando na implementação
            do protocolo, sendo executado sempre que o agente receber
            uma mensagem do tipo FIPA_AGREE

            Parâmetros
            ----------
            message : Mensagem FIPA-ACL
        """
        pass

    def handle_failure(self, message):
        """
            handle_failure
            --------------

            Este método deve ser sobrescrito quando na implementação
            do protocolo, sendo executado sempre que o agente receber
            uma mensagem do tipo FIPA_FAILURE

            Parâmetros
            ----------
            message : Mensagem FIPA-ACL
        """
        pass

    def handle_inform(self, message):
        """
            handle_inform
            -------------

            Este método deve ser sobrescrito quando na implementação
            do protocolo, sendo executado sempre que o agente receber
            uma mensagem do tipo FIPA_INFORM

            Parâmetros
            ----------
            message : Mensagem FIPA-ACL
        """
        pass

    def execute(self, message):
        """
            execute
            -------

            Este método sobrescreve o metodo execute da classe 
            Behaviour. Nele esta implementado a seleção de qual
            método será executado logo após o recebimento de uma
            mensagem

            Parâmetros
            ----------
            message : Mensagem FIPA-ACL
        """

        self.message = message

        if self.filter_protocol.filter(self.message):

            if self.filter_Request.filter(self.message):
                self.handle_request(message)

            elif self.filter_refuse.filter(self.message):
                self.handle_refuse(message)

            elif self.filter_Agree.filter(self.message):
                self.handle_agree(message)

            elif self.filter_failure.filter(self.message):
                self.handle_failure(message)

            elif self.filter_inform.filter(self.message):
                self.handle_inform(message)

            else:
                return
        else:
            return


class FipaContractNetProtocol(Behaviour):

    """
        FipaContractNetProtocol
        -------------------------

        Classe que implementa o protocolo FipaContractNetProtocol
        herdando a classe Behaviour e implementando seus métodos
    """

    def __init__(self, agent, message=None, is_initiator=True):
        """
            Inicializa a classe que implementa o protocolo
            FipaContractNetProtocol

            Parâmetros
            ----------
            agent : instância do agente que executara os comportamentos
                    estebelecidos pelo protocolo
            message : mensagem a ser enviada pelo agente quando o 
                      parâmetro is_initiator for verdadeiro
            is_initiator : parâmetro do tipo booleano que indica se esta 
                          instancia do protocolo agirá como Initiator
                          ou como participante

        """
        super(FipaContractNetProtocol, self).__init__(agent)

        self.is_initiator = is_initiator
        self.cfp_qtd = 0
        self.received_qtd = 0

        self.proposes = []

        self.message = message

        self.filter_protocol = Filter()
        self.filter_protocol.set_protocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)

        self.received_cfp
        filter_cfp = Filter()
        self.received_cfp
        filter_cfp.set_performative(ACLMessage.CFP)

        self.filter_refuse = Filter()
        self.filter_refuse.set_performative(ACLMessage.REFUSE)

        self.filter_propose = Filter()
        self.filter_propose.set_performative(ACLMessage.PROPOSE)

        self.filter_accept_propose = Filter()
        self.filter_accept_propose.set_performative(ACLMessage.ACCEPT_PROPOSAL)

        self.filter_reject_propose = Filter()
        self.filter_reject_propose.set_performative(ACLMessage.REJECT_PROPOSAL)

        self.filter_failure = Filter()
        self.filter_failure.set_performative(ACLMessage.FAILURE)

        self.filter_inform = Filter()
        self.filter_inform.set_performative(ACLMessage.INFORM)

    def on_start(self):
        """
            on_start
            --------

            Este método sobrescreve o metoso on_start da classe
            Behaviour e implementa configurações adicionais
            à inicialização do protocolo FipaContractNetProtocol
        """
        Behaviour.on_start(self)

        if self.is_initiator and self.message != None:

            if self.message.performative == ACLMessage.CFP:

                self.cfp_qtd = len(self.message.receivers)

                self.agent.send(self.message)

                self.timed_behaviour()

    def handle_cfp(self, message):
        """
            handle_cfp
            ----------

            Este método deve ser sobrescrito quando na implementação
            do protocolo, sendo executado sempre que o agente receber
            uma mensagem do tipo FIPA_CFP

            Parâmetros
            ----------
            message : Mensagem FIPA-ACL
        """
        pass

    def handle_propose(self, message):
        """
            handle_propose
            --------------

            Este método deve ser sobrescrito quando na implementação
            do protocolo, sendo executado sempre que o agente receber
            uma mensagem do tipo FIPA_PROPOSE

            Parâmetros
            ----------
            message : Mensagem FIPA-ACL
        """
        self.received_qtd += 1

    def handle_refuse(self, message):
        """
            handle_refuse
            -------------

            Este método deve ser sobrescrito quando na implementação
            do protocolo, sendo executado sempre que o agente receber
            uma mensagem do tipo FIPA_REFUSE

            Parâmetros
            ----------
            message : Mensagem FIPA-ACL
        """
        self.received_qtd += 1

    def handle_all_proposes(self, proposes):
        """
            handle_all_proposes
            -------------------

            Este método deve ser sobrescrito quando na implementação
            do protocolo, sendo executado em um dos dois casos:
            * A quantidade de respostas recebidas for igual a quantidade
            de solicitações recebidas
            * O timeout for atingido

            Parâmetros
            ----------
            proposes : lista com as respostas das solicitações envidas
                       pelo Initiator
        """
        pass

    def handle_inform(self, message):
        """
            handle_inform
            -------------

            Este método deve ser sobrescrito quando na implementação
            do protocolo, sendo executado sempre que o agente receber
            uma mensagem do tipo FIPA_INFORM

            Parâmetros
            ----------
            message : Mensagem FIPA-ACL
        """
        pass

    def handle_reject_proposes(self, message):
        """
            handle_reject_proposes
            ----------------------

            Este método deve ser sobrescrito quando na implementação
            do protocolo, sendo executado sempre que o agente receber
            uma mensagem do tipo FIPA_REJECT_PROPOSE

            Parâmetros
            ----------
            message : Mensagem FIPA-ACL
        """
        pass

    def handle_accept_propose(self, message):
        """
            handle_accept_propose
            ---------------------

            Este método deve ser sobrescrito quando na implementação
            do protocolo, sendo executado sempre que o agente receber
            uma mensagem do tipo FIPA_ACCEPT_PROPOSE

            Parâmetros
            ----------
            message : Mensagem FIPA-ACL
        """
        pass

    def timed_behaviour(self):
        """
            timed_behaviour
            ---------------

            Este método é implementado sempre que o protocolo a ser 
            implementado necessitar de restrições temporais, como é
            o caso do FipaContractNetProtocol. Neste caso ele faz
            uso do metodo callLater do twisted que recebe como 
            parâmetro um método e o atrazo de tempo para que este
            método seja executado

        """
        Behaviour.timed_behaviour(self)

        twisted.internet.reactor.callLater(self.timeout,
                                           self.execute_on_timeout)

    def execute_on_timeout(self):
        """
            execute_on_timeout
            ------------------

            Este método executa o método handle_all_proposes caso nem
            todas as mensagens FIPA_CFP enviadas pelo agente obtenham
            resposta
        """
        if not self.received_qtd == self.cfp_qtd:
            self.handle_all_proposes(self.proposes)

    def execute(self, message):
        """
            execute
            -------

            Este método sobrescreve o metodo execute da classe 
            Behaviour. Nele esta implementado a seleção de qual
            método será executado logo após o recebimento de uma
            mensagem

            Parâmetros
            ----------
            message : Mensagem FIPA-ACL
        """

        Behaviour.execute(self, message)

        self.message = message

        if self.filter_protocol.filter(self.message):
            if self.filter_cfp.filter(self.message):
                self.handle_cfp(message)

            elif self.filter_propose.filter(self.message):
                self.proposes.append(message)
                self.handle_propose(message)

                if self.received_qtd == self.cfp_qtd:
                    self.handle_all_proposes(self.proposes)

            elif self.filter_refuse.filter(self.message):
                self.proposes.append(message)
                self.handle_refuse(message)

                if self.received_qtd == self.cfp_qtd:
                    self.handle_all_proposes(self.proposes)

            elif self.filter_accept_propose.filter(self.message):
                self.handle_accept_propose(message)

            elif self.filter_reject_propose.filter(self.message):
                self.handle_reject_proposes(message)

            elif self.filter_failure.filter(self.message):
                self.handle_failure(message)

            elif self.filter_inform.filter(self.message):
                self.handle_inform(message)

            else:
                return

        else:
            return

class FipaSubscribeProtocol(Behaviour):
    """
        FipaSubscribeProtocol
        ---------------------

        Classe que implementa o protocolo FipaSubscribeProtocol
        herdando a classe Behaviour e implementando seus métodos
    """

    def __init__(self, agent, message=None, is_initiator=True):
        """
            método de inicialização
            -----------------------


        """

        super(FipaSubscribeProtocol, self).__init__(agent)

        self.is_initiator = is_initiator
        self.message = message

        self.subscribers = set()

        self.filter_protocol = Filter()
        self.filter_protocol.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)

        self.filter_subscribe = Filter()
        self.filter_subscribe.set_performative(ACLMessage.SUBSCRIBE)

        self.filter_agree = Filter()
        self.filter_agree.set_performative(ACLMessage.AGREE)

        self.filter_inform = Filter()
        self.filter_inform.set_performative(ACLMessage.INFORM)

        self.filter_refuse = Filter()
        self.filter_refuse.set_performative(ACLMessage.REFUSE)

        self.filter_cancel = Filter()
        self.filter_cancel.set_performative(ACLMessage.CANCEL)

        self.filter_failure = Filter()
        self.filter_failure.set_performative(ACLMessage.FAILURE)

    def on_start(self):
        """
            on_start
            --------

            Este método sobrescreve o metoso on_start da classe
            Behaviour e implementa configurações adicionais
            à inicialização do protocolo FipaContractNetProtocol
        """
        Behaviour.on_start(self)

        if self.is_initiator and self.message != None:

            if self.message.performative == ACLMessage.SUBSCRIBE:
                self.agent.send(self.message)
                #self.timed_behaviour()

    def handle_subscribe(self, message):
        """
            handle_subscribe
            ----------------
        """
        pass

    def handle_agree(self, message):
        """
            handle_agree
            ------------
        """
        pass

    def handle_refuse(self, message):
        """
            handle_refuse
            -------------
        """
        pass

    def handle_inform(self, message):
        """
            handle_inform
            -------------
        """
        pass

    def handle_cancel(self, message):
        """
            handle_cancel
            -------------
        """
        pass

    def execute(self, message):
        """
            execute
            -------

            Este método sobrescreve o metodo execute da classe 
            Behaviour. Nele esta implementado a seleção de qual
            método será executado logo após o recebimento de uma
            mensagem

            Parâmetros
            ----------
            message : Mensagem FIPA-ACL
        """

        Behaviour.execute(self, message)

        self.message = message

        if self.filter_protocol.filter(self.message):
            if self.filter_subscribe.filter(self.message):
                self.handle_subscribe(message)

            elif self.filter_cancel.filter(self.message):
                self.handle_cancel(message)

            elif self.filter_inform.filter(self.message):
                self.handle_inform(message)

            elif self.filter_agree.filter(self.message):
                self.handle_agree(message)

            elif self.filter_failure.filter(self.message):
                self.handle_failure(message)
            else:
                return

        else:
            return

    def register(self, aid):
        """
            register
            --------
        """
        self.subscribers.add(aid)

    def deregister(self, aid):
        """
            deregister
            ----------
        """
        self.subscribers.remove(aid)

    def notify(self, message):
        """
            notify
            ------
        """
        for sub in self.subscribers:
            message.add_receiver(sub)
        self.agent.send(message)
