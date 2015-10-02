Enviando Objetos
================

Nem sempre o que é preciso enviar para outros agentes pode ser representado por texto simpes não é mesmo!

Para enviar objetos encapsulados no content de mensagens FIPA-ACL com PADE basta utilizar o módulo nativo do Python *pickle*.

Enviando objetos serializados com pickle
----------------------------------------

Para enviar um objeto serializado com piclke basta seguir os passos:

::

    import pickle

*pickle* é uma biblioteca para serialização de objetos, assim, para serializar um objeto qualquer, utilize `pickle.dumps()`, veja:

::

    dados = {'nome' : 'agente_consumidor', 'porta' : 2004}
    dados_serial = pickle.dumps(dados)
    message.set_content(dados_serial)

Pronto! O objeto já pode ser enviado no conteúdo da mensagem. 

Recebendo objetos serializados com pickle
----------------------------------------

Agora para receber o objeto, basta carregá-lo utilizando o comando:

::

    dados_serial = message.content
    dados = pickle.loads(dados_serial)

Simples assim ;)