Alô Mundo
=========

PADE foi implementado com um objetivo central: simplicidade!

Depois de ter o PADE instalado em seu computador fica bem simples começar a trabalhar.

Em uma pasta crie um arquivo chamado start_ams.py com o seu editor de texto preferido, e copie e cole o seguinte trecho de código dentro dele:

::

    # este e o arquivo start_ams.py
    from pade.misc.common import set_ams, start_loop

    if __name__ == '__main__':
        set_ams('localhost', 8000)
        start_loop(list(), gui=True)

A essa altura você já deve estar vendo a interface gráfica de monitoramento dos agentes em Python, assim como essa:

.. figure:: ../img/InterfaceSniffer.png
    :align: center
    :width: 5.0in
    



    
