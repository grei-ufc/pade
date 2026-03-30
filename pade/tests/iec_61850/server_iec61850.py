#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import threading
import traceback
import signal

# Garante que ele ache a biblioteca na mesma pasta
sys.path.append('.')
# CORREÇÃO AQUI: Importa com o prefixo 'py' e cria um apelido 'iec61850'
import pyiec61850 as iec61850

def signal_handler(sig, frame):
    global running
    running = 0
    print('\n[Servidor IEC] Desligamento solicitado (Ctrl+C). Encerrando...')

signal.signal(signal.SIGINT, signal_handler)
tcpPort = 8102
running = 1

class myIECServer():
    def __init__(self):
        self.__model = iec61850.IedModel_create('testmodel')
        lDevice1 = iec61850.LogicalDevice_create('SENSORS', self.__model)
        
        lln0 = iec61850.LogicalNode_create('LLN0', lDevice1)
        ttmp1 = iec61850.LogicalNode_create('TTMP1', lDevice1)
        
        # Variáveis de Leitura (SAV) e Escrita (ASG)
        iec61850.CDC_SAV_create('TmpSv',  iec61850.toModelNode(ttmp1), 0, False)
        iec61850.CDC_ASG_create('TmpSp',  iec61850.toModelNode(ttmp1), 0, False)
        
        self.__iedServer = iec61850.IedServer_create(self.__model)
        iec61850.IedServer_start(self.__iedServer, tcpPort)
        
        if not iec61850.IedServer_isRunning(self.__iedServer):
            print('[Erro] Falha ao iniciar o servidor IED IEC 61850!\n')
            iec61850.IedServer_destroy(self.__iedServer)
            sys.exit(-1)
            
        print(f"🏭 [Servidor IED] Online e escutando na porta TCP {tcpPort}...")

    def run(self):
        global running
        while running:
            time.sleep(0.1)
        self.stop()

    def stop(self):
        iec61850.IedServer_stop(self.__iedServer)
        iec61850.IedServer_destroy(self.__iedServer)
        iec61850.IedModel_destroy(self.__model)
        print("🔌 [Servidor IED] Parado com sucesso.")

if __name__ == '__main__':
    try:
        srv = myIECServer()
        srvThread = threading.Thread(target=srv.run)
        srvThread.start()
        while running:
            time.sleep(1)
    except Exception as e:
        running = 0
        print("Erro Crítico:")
        traceback.print_exc(file=sys.stdout)
        sys.exit(-1)