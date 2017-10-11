Estrutura construtiva do PADE
=============================

Este guia está sendo desenvolvido com o objetivo de auxiliar o desenvolvimento do PADE, fornecendo compreenssão a respeito da estrutura construtiva do PADE.

PADE passará por alterações profundas entre suas versões 1.0 e 2.0. Como a versão 1.0 já está em sua versão estável tendo sido utilizada em diversas aplicações com exito, e não sendo mais objeto de desenvolvimento, essa documentação irá focar nas nova estrutura do PADE que, como mencionado, passou por profundas alterações internas.

Características do PADE 1.0
---------------------------

Apesar de muitas alterações estarem sendo implementadas para a versão 2.0, é necessário verificar e revisar alguns aspectos da versão 1.0 que fornecem a base do desenvolvimento do PADE e não deverão ser alterados.

Primeiramente é necessário mencionar que o PADE é desenvolvido utilizando o framework twisted, que segundo descrição encontrada no site do twisted:

    Twisted is an event-driven networking engine written in Python and licensed under the open source

Twisted é um framework para implementação de aplicações distribuídas que utilizem protocolos padrões, como http, ftp, ssh, ou protocolos personalizados. PADE faz uso do twisted por meio da segunda opção, implementando protocolos personalizados, tanto para troca de mensagens de controle interno, quanto para fornecer uma interface aos protocolos descritos pelo padão FIPA.

Pacote core
-----------

A essencia do desenvolvimento do Twisted está contida no pacote *core*. O pacote core, por sua vez possui quatro módulos:

- __init__.py: torna uma pasta um pacote;

- agent.py: contém as classes que implementam as funcionalidades necessárias para a definição dos agentes e para possibilitar registro no AMS, verificação de conexão e troca de mensagens;

- new_ams.py: implementa o agente AMS e seus comportamentos;

- peer.py: implementa comportamentos básicos do protocolo twisted para troca de mensagens. 

Sendo assim, como PADE é desenvolvido com Twisted, precisa obdecer sua estrutura de classes. No Twisted, duas classes são essenciais: 

1. Uma classe para implementar o protocolo propriamente dito, que trata as mensagens recebidas por um ponto comunicante e envia as mensagens para outro ponto comunicante.

2. Uma classe para implementar o protocolo definido na primeira classe, essa classe é chamada de classe Factory.

Na versão 1.0 do pade, a definição dessas classes estavam presentes no módulo agent.py, mas por uma questão de organização do código, a classe que implementa o protocolo foi transferida para o módulo peer.py e chamasse agora **PeerProtocol** extendendo a classe do twisted **LineReceiver**.

Módulo agente.py
~~~~~~~~~~~~~~~~

No módulo agent.py estão presentes as seguintes classes:

- **AgentProtocol**: Essa classe herda a classe PeerProtocol que é importada do módulo peer.py e extende alguns de seus métodos, tais como connectionMade, connectionLost, send_message e lineReceived.

- **AgentFactory**: Essa classe herda a classe ClientFactory do módulo protocol importado do Twisted, implementando o método buildProtocol, clientConnectionFailed e clientConnectionLost, muito importantes para funcionamento do sistema multiagente. Nessa classe temos importantes atributos, tais como messages, react, ams_aid, on_start e table.

- **Agent\_**: Essa classe estabelece as funcionalidades essenciais de um agente como: conexão com o AMS; configurações iniciais; envio de mensagens e adição de comportamentos. Os atributos presentes nesta classe são: aid, debug, ams, agentInstance, behaviours, system_behaviours.
Os metodos presentes nesta classe são:
send: utilizado para o envio de mensagens entre agentes
call_later: utilizado para executar metodos apos periodo especificado;
send_to_all: envia mensagem a todos os agentes registrados na tabela do agente;
add_all: adiciona todos os agentes presentes na tabela dos agentes;
on_start: a ser utilizado na implementação dos comportamentos iniciais;
react: a ser utlizado na implementação dos comportamentos dos agentes quando recebem uma mensagem.

Para a descrição das demais classes cabe aqui uma breve explicação. Na versão 1.0 as mensagens de controle internas do PADE eram enviadas sem nenhuma padronização, aproveitando somente a infraestrutura que o twisted monta para executar suas aplicações distribuídas. Isso deixava o código sujo, commuitos ifs e elses, dificultando seu entendimento e manutenabilidade.

Uma das alterações mais profundas na versão 2.0 é que toda essa estrutura de troca de mensagens internas agora faz uso e obedece as classes que implementam os protocolos de comunicação FIPA. Isso deixou o código mais organizado e criou a oportunidade de implementar algumas melhorias na lógica de execução. Sendo assim, o comportamento de atualização das tabelas que cada agente tem com os endereços dos agentes presentes na plataforma foi implementado com um protocolo FIPASubscribe que realiza o paradigma de comunicação editor-assinante, em que o agente AMS é o agente editor e todos os outros agentes da plataforma são os assinantes. Também o comportamento de verificação se o agente está ativo ou não foi modelado como um protocolo FIPA request, em que o AMS solicita a cada um dos agentes sua resposta, caso a resposta não venha, significa que o agente não está mais ativo. 

- **SubscribeBehaviour**: Classe que implementa o lado subscriber do protocolo Publisher/Subscriber para atualização das tabelas de agentes.

- **CompConnection**: Classe que implementa o comportamento de verificação de atividade dos agentes.

- **Agent**: Pode ser considerada a classe mais importante do módulo agent.py pois é extendendo esta classe que um agente é definido no PADE. Dois métodos são definidos nesta classe: o primeiro é o método de inicialização padão de classes em Python, onde são instanciadas as classes dos protocolos padrões do PADE que irão realizar a identificação do agente junto ao AMS e também inscrever este agente como assinante do AMS em seu comportamento de verificação de atividade dos agente (se o agente está ou não em funcionamento). O segundo método, não menos importante, envia todas as mensagens que recebe ao AMS, para que sejam armazenas em um banco de dados e estejam disponíveis para consulta pelo administrador do sistema multiagente por meio da interface web ou do acesso direto ao banco de dados.

Módulo new_ams.py
~~~~~~~~~~~~~~~~

Este módulo é uma adição do PADE 2.0. Na versão 1.0 o comportamento do AMS estava contido dentro do módulo ams.py que implementava um protocolo com as classes do Twisted exclusivamente para o agente AMS e também para o agente Sniffer que deixou de existir na versão 2.0, pois o comportamento de envio de mensagens para armazenamento já está embutido no comportamento do próprio agente que não precisa mais ser solicitado por mensagens, uma vez que assim que uma mensagem é recebida pelo agente ela é enviada automaticamente para o AMS, que armazena a mensagem em um banco de dados especificado.

No módulo new_ams as seguintes classes são implementadas:

- **ComportSendConnMessages**: Conportamento temporal que envia mensagens a cada 4,0 segundos para verificar se o agente está conectado.

- **ComportVerifyConnTimed**: Comportamento temporal que a cada 10,0 segundos verifica o intervalo de tempo de respostas do comportamento ComportSendConnMessages. Se o intervalo de tempo da ultima resposta for maior que 10,0 segundos o agente AMS considera que o agente não está mais ativo e retira o agente da tabela de agentes vigente. 

- **CompConnectionVerify**: Protocolo Request que recebe as mensagens de resposta dos agentes que têm sua conexão verificada.

- **PublisherBehaviour**: Protocolo Publisher-Subscribe em que o AMS é o publisher e publica uma nova tabela de agentes sempre que um novo agente ingressa na plataforma, ou que algum agente existente tem sua desconexão detectada.

- **AMS**: Classe que declara todos os comportamentos relacionados ao agente AMS, como verificação de conexão e publicação das tabelas de agentes, além de receber e armazenar as mensagens recebidas por todos os agentes presentes na plataforma.

Pacote misc
-----------

O pacote misc armazena módulos com diferentes propósitos gerais. Até o presente desenvolvimento, o pacote misc tem dois módulos principais, são eles:
- common.py
- utility.py

Começando pelo mais simples, o módulo utility.py tem como propópito oferecer métodos com facilidades para o desenvolvimento, o único método disponível é o método display_message() que imprime uma mensagem  na tela, passada como parâmetro para o método, com data, horário e nome do agente.

O segundo módulo do pacote misc é o módulo common.py que fornece ao usuário do PADE métodos e objetos de propósito geral que têm relação com a inicialização de uma sessão multiagente PADE. Neste módulo estão presentes as classes FlaskServerProcess que inicializa o serviço web desenvolvido com o framework Flask. A outra classe do módulo é a classe PadeSession, que define as sessões a serem lançadas no ambiente de execução PADE. Essa classe tem uma das mais importantes funções no PADE que é a de inicializar o loop de execução do PADE. Ou seja, quando se pretende lançar agentes no ambiente de execução do PADE, o procedimento é o seguinte:

::

    # importações necessarias:
    from pade.misc.utility import display_message
    from pade.misc.common import PadeSession
    from pade.core.agent import Agent
    from pade.acl.aid import AID

    # definicao dos agentes por meio das classes Agent e de
    # classes associadas a comportamentos ou protocolos

    class AgenteHelloWorld(Agent):
        def __init__(self, aid):
            super(AgenteHelloWorld, self).__init__(aid=aid, debug=True)
            display_message(self.aid.localname, 'Hello World!')

    # definicao do metodo para inicializacao dos agentes:
    def config_agents():

        agents = list()

        agente_hello = AgenteHelloWorld(AID(name='agente_hello'))
        agents.append(agente_hello)

        # declaracao do objeto PadeSession
        s = PadeSession()
        # adicao da lista de agentes 
        s.add_all_agents(agents)
        # registro de usuarios na plataforma
        s.register_user(username='lucassm', email='lucas@gmail.com', password='12345')

        return s

    # inicializacao dos ambiente de execucao 
    # propriamente dito:
    if __name__ == '__main__':

        s = config_agents()
        # inicializacao do loop de execucao Pade
        s.start_loop()

Como pode ser observado por meio deste exemplo, é no método config_agents() que os agentes são instanciados, assim como o objeto PadeSession(), que logo em seguida tem seu método add_all_agents() chamado e recebe como parâmetro uma lista com as instancias dos agentes. Em seguida é chamado o método register_user() para registrar um usuario. O objeto PadeSession é retornado pelo método config_agents(), que é chamado no corpo principal desse script e atribuído a variável s, que logo em seguida, chama o método start_loop() do objeto PadeSession retornado. 

Nesse simples exemplo é possível observar a importancia da classe PadeSession, que recebe as instancias dos agentes a serem lançados, registra usuarios da sessão e inicializa o loop de execussão do PADE.

Aqui cabe um questionamento essencial para o ambiente de execução de agentes PADE. E se quisermos lançar agentes em uma sessão PADE já iniciada, como faremos?

A primeira coisa a ser definida aqui é que após iniciada a sessão, não será possível registrar usuários e os agentes lançados, só poderão entrar na plataforma se forem utilizadas credenciais de usuários já registrados.
