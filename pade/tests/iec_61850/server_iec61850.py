#!/usr/bin/env python3

"""Simple IEC 61850 server used by the PADE integration example."""

import sys
import time
import threading
import traceback
import signal

try:
    import pyiec61850 as iec61850
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Missing optional dependency 'pyiec61850'. "
        "Install it in the active environment before starting the IEC 61850 server."
    ) from exc

def signal_handler(sig, frame):
    global running
    running = 0
    print('\n[IEC Server] Shutdown requested (Ctrl+C). Stopping...')

signal.signal(signal.SIGINT, signal_handler)
tcpPort = 8102
running = 1

class myIECServer():
    def __init__(self):
        self.__model = iec61850.IedModel_create('testmodel')
        lDevice1 = iec61850.LogicalDevice_create('SENSORS', self.__model)

        lln0 = iec61850.LogicalNode_create('LLN0', lDevice1)
        ttmp1 = iec61850.LogicalNode_create('TTMP1', lDevice1)

        # Readable sensor values and writable setpoint values.
        iec61850.CDC_SAV_create('TmpSv',  iec61850.toModelNode(ttmp1), 0, False)
        iec61850.CDC_ASG_create('TmpSp',  iec61850.toModelNode(ttmp1), 0, False)

        self.__iedServer = iec61850.IedServer_create(self.__model)
        iec61850.IedServer_start(self.__iedServer, tcpPort)

        if not iec61850.IedServer_isRunning(self.__iedServer):
            print('[Error] Failed to start the IEC 61850 IED server.\n')
            iec61850.IedServer_destroy(self.__iedServer)
            sys.exit(-1)

        print(f"[IED Server] Online and listening on TCP port {tcpPort}.")

    def run(self):
        global running
        while running:
            time.sleep(0.1)
        self.stop()

    def stop(self):
        iec61850.IedServer_stop(self.__iedServer)
        iec61850.IedServer_destroy(self.__iedServer)
        iec61850.IedModel_destroy(self.__model)
        print("[IED Server] Stopped successfully.")


if __name__ == '__main__':
    try:
        srv = myIECServer()
        srvThread = threading.Thread(target=srv.run)
        srvThread.start()
        while running:
            time.sleep(1)
    except Exception:
        running = 0
        print("Critical error:")
        traceback.print_exc(file=sys.stdout)
        sys.exit(-1)
