Enviando Objetos
================

Nem sempre o conteúdo de uma mensagem pode ser representado apenas por
texto simples. Em aplicações científicas, por exemplo, é comum trafegar
dicionários, listas ou estruturas numéricas serializadas.

No PADE, uma forma prática de fazer isso é usar o módulo nativo
``pickle``.

Serializando objetos com ``pickle``
-----------------------------------

Primeiro, importe o módulo:

::

    import pickle

Depois serialize o objeto desejado com ``pickle.dumps()``:

::

    dados = {'nome': 'agente_consumidor', 'porta': 2004}
    dados_serializados = pickle.dumps(dados)
    message.set_content(dados_serializados)

Pronto: o objeto já pode ser enviado no campo ``content`` da mensagem
ACL.

Recebendo o objeto
------------------

Do lado receptor, basta desserializar com ``pickle.loads()``:

::

    import pickle

    dados_serializados = message.content
    dados = pickle.loads(dados_serializados)

    print(dados['nome'])

Observações sobre logs e depuração
----------------------------------

Quando conteúdos binários trafegam pela rede:

* o agente receptor continua recebendo os bytes corretos em
  ``message.content``;
* a visualização no terminal pode mostrar uma representação resumida do
  conteúdo;
* os logs CSV preservam o registro da mensagem sem depender de SQLite.

Esse padrão é especialmente útil quando o PADE é usado em integração com
co-simulações ou estruturas matemáticas mais complexas.
