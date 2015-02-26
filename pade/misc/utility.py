from datetime import datetime

def display_message(name, data):
    """
        Metodo utilizado para exibicao de mensagens no console de comandos
    """
    date = datetime.now()
    date = date.strftime('%d/%m/%Y %H:%M:%S --> ')
    print '[' + name + '] ' + date + str(data)
