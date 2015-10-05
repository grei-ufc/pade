Interface Gráfica
=================

Para ativar a funcionalidade de interface gráfica do PADE é bem simples, basta passar o parâmetro *gui=True* na função 
::

    start_loop(agentes, gui=True)

A interface gráfica do PADE ainda está bem simples e sem muitas funcionalidades, implementada com base no framework para desenvolvimento de GUI Qt/PySide, isso gera ulgumas complicações. Para a versão 2.0 será implementada uma interface web com base no framework `Flask <http://flask.pocoo.org/>`_, mais completa e funcional.