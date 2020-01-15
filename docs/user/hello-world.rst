Alô Mundo
=========

PADE foi implementado com um objetivo central: simplicidade!

Depois de ter o PADE instalado em seu computador fica bem simples começar a trabalhar.

Em uma pasta crie um arquivo chamado start_ams.py com o seu editor de texto preferido, e copie e cole o seguinte trecho de código dentro dele:

::

    from pade.misc.common import PadeSession

    def config_agents():

        agents = list()

        s = PadeSession()
        s.add_all_agents(agents)
        s.register_user(username='pade_user', email='user@pade.com', password='12345')

        return s

    if __name__ == '__main__':

        s = config_agents()
        s.start_loop()

A essa altura você já deve estar vendo a interface gráfica de monitoramento dos agentes em Python, assim como essa:

.. figure:: ../img/InterfaceSniffer.png
    :align: center
    :width: 5.0in
    



    
