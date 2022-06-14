import logging
import typing

from PyQt5 import QtCore, QtWidgets,QtGui
import sys, time

from modbusTCP_DB.modbusTCPService import *
from modbusTCP_DB.modbusRTUService import *
from modbusTCP_DB.OpcUAService import *
from modbusTCP_DB.TimeSeriesDatabase import *

from modbusTCP_DB.config.ConfigMB import *
from modbusTCP_DB.config.ConfigDB import *
from modbusTCP_DB.config.ConfigUA import *


class ServiceThread(QtCore.QThread):
    mb_update_signal = QtCore.pyqtSignal()
    mb_state_signal = QtCore.pyqtSignal(int)
    opc_state_signal = QtCore.pyqtSignal(int)
    db_state_signal = QtCore.pyqtSignal(int)
    #updated = QtCore.pyqtSignal()

    def __init__(self, conf_ua: ConfigUA, conf_db: ConfigDB, conf_mb: ConfigMB):
        super(ServiceThread, self).__init__(None)
        self.conf_ua = conf_ua
        self.conf_db = conf_db
        self.conf_mb = conf_mb
        self.is_running = False

        self.opc_server_state = 0
        self.db_logging_state = 0
        self.mbtcp_server_state = 0
        self.mbrtu_server_state = 0

        self.opc_server_cmd = 0 # 0 = Nothing - 1 = Run - 2 = Stop
        self.db_logging_cmd = 0
        self.mbtcp_server_cmd = 0
        self.mbrtu_server_cmd = 0

        self.modbusServicesRTU = []
        self.modbusServicesTCP = []
        self.devices = []
        for device in self.conf_mb.CONFIG_EQ:
            if(device.type == 'rtu'):
                self.modbusServicesRTU.append(ModbusRTUService(dev_modbus=device))
            else:
                self.modbusServicesTCP.append(ModbusTCPService(dev_modbus=device))
            self.devices.append(device)

        self.ts_database: TimeSeriesDatabase
        self.server_opc: OpcUAService


    def run(self):
        self.is_running = True
        logging.info('Starting thread...')
        cnt = 0
        while (True):
            cnt += 1
            if cnt == 99:
                cnt = 0
                logging.info("Thread running...")
            self._service_modbus()
            self._service_opc()
            self._service_db()
            time.sleep(1)
            #self.any_signal.emit(cnt)

    def stop(self):
        self.is_running = False
        print('Stopping thread...')
        self.terminate()

    def _service_modbus(self):

        # Estados
        if(self.mbtcp_server_state == 0): #No iniciado
            self.mbtcp_server_state = 0 # No hago nada
        elif(self.mbtcp_server_state == 1): # Estado running
            try:
                for service in self.modbusServicesTCP:
                    service.update()
                self.mb_update_signal.emit()
            except:
                logging.error(f"modbus service - error al actualizar dispositivos", self.mbtcp_server_state)
                self.mbtcp_server_state = 2
                self.mbtcp_server_cmd = 0
                self.mb_state_signal.emit(self.mbtcp_server_state)

        elif(self.mbtcp_server_state == 2): # Estado stopped
            self.mbtcp_server_state = 2

        # Comandos
        if(self.mbtcp_server_cmd == 0):
            self.mbtcp_server_cmd = 0  # No hago nada
        elif(self.mbtcp_server_cmd == 1): #Start
            self.mbtcp_server_state = 1
            self.mbtcp_server_cmd = 0
            self.mb_state_signal.emit(self.mbtcp_server_state)
        elif (self.mbtcp_server_cmd == 2):  # Stop
            self.mbtcp_server_state = 2
            self.mbtcp_server_cmd = 0
            self.mb_state_signal.emit(self.mbtcp_server_state)

    def _service_opc(self):
        logging.info(f"opc service state %i", self.opc_server_state)
        # Estados
        if (self.opc_server_state == 0):  # No iniciado
            self.opc_server_state = 0  # No hago nada
        elif (self.opc_server_state == 1):  # Estado running
            self.server_opc.task()
        elif (self.opc_server_state == 2):  # Estado stopped
            self.opc_server_state = 2

        # Comandos
        if (self.opc_server_cmd == 0):
            self.opc_server_cmd = 0  # No hago nada
        elif (self.opc_server_cmd == 1):  # Start
            if self.opc_server_state == 0:
                self.server_opc = OpcUAService(devices=self.devices, conf_ua=self.conf_ua.conf_ua)
            self.opc_server_state = 1
            self.opc_server_cmd = 0
            self.opc_state_signal.emit(self.opc_server_state)
        elif (self.opc_server_cmd == 2):  # Stop
            self.opc_server_state = 2
            self.opc_server_cmd = 0
            self.opc_state_signal.emit(self.opc_server_state)

    def _service_db(self):
        # Estados
        if (self.db_logging_state == 0):  # No iniciado
            self.db_logging_state = 0  # No hago nada
        elif (self.db_logging_state == 1):  # Estado running
            self.ts_database.task()
        elif (self.db_logging_state == 2):  # Estado stopped
            self.db_logging_state = 2

        # Comandos
        if (self.db_logging_cmd == 0):
            self.db_logging_cmd = 0  # No hago nada

        elif (self.db_logging_cmd == 1):  # Start
            if self.db_logging_state == 0:
                self.ts_database = TimeSeriesDatabase(devices=self.devices, db_conf=self.conf_db.db_conf)
            self.db_logging_state = 1
            self.db_logging_cmd = 0
            self.db_state_signal.emit(self.db_logging_state)

        elif (self.db_logging_cmd == 2):  # Stop
            self.db_logging_state = 2
            self.db_logging_cmd = 0
            self.db_state_signal.emit(self.db_logging_state)

    def write_float_reg(self, variable:str, value, idx):
        logging.info("Thread writing modbus dev id %s var %s value = %s ", str(idx), str(variable), str(value))
        self.modbusServicesTCP[idx].write_value(variable, value)



class ThreadModbusTCP(QtCore.QThread):
    any_signal = QtCore.pyqtSignal(int)
    #updated = QtCore.pyqtSignal(typing.List[ModbusTCPService])

    def __init__(self, services: typing.List[ModbusTCPService]):
        super(ThreadModbusTCP, self).__init__(None)
        self.services = services
        self.is_running = True


    def run(self):
        print('Starting thread...')
        cnt = 0
        while (True):
            cnt += 1
            if cnt == 99:
                cnt = 0

            for service in self.services:
                service.update()


            time.sleep(1)
            #self.any_signal.emit(cnt)

    def stop(self):
        self.is_running = False
        print('Stopping thread...')
        self.terminate()

class ThreadModbusRTU(QtCore.QThread):
    any_signal = QtCore.pyqtSignal(int)

    def __init__(self, services: typing.List[ModbusRTUService]):
        super(ThreadModbusRTU, self).__init__(None)
        self.services = services
        self.is_running = True

    def run(self):
        print('Starting thread...')
        cnt = 0
        while (True):
            cnt += 1
            if cnt == 99:
                cnt = 0

            for service in self.services:
                service.update()

            time.sleep(1)
            #self.any_signal.emit(cnt)

    def stop(self):
        self.is_running = False
        print('Stopping thread...')
        self.terminate()


class ThreadOPC(QtCore.QThread):
    any_signal = QtCore.pyqtSignal(int)
    def __init__(self, opc: OpcUAService):
        super(ThreadOPC, self).__init__(None)
        self.server_opc = opc
        self.is_running = True

    def run(self):
        print('Starting thread...')
        self.server_opc.start()
        cnt = 0
        while (True):
            cnt += 1
            if cnt == 99:
                cnt = 0

            self.server_opc.task()

            time.sleep(1)
            # self.any_signal.emit(cnt)

    def stop(self):
        self.is_running = False
        print('Stopping thread...')
        # cierro conexion
        self.server_opc.stop()
        self.terminate()


class ThreadDatabase(QtCore.QThread):
    any_signal = QtCore.pyqtSignal(int)

    def __init__(self, db: TimeSeriesDatabase):
        super(ThreadDatabase, self).__init__(None)
        self.server_db = db
        self.is_running = True

    def run(self):
        print('Starting thread...')
        cnt = 0
        while (True):
            cnt += 1
            if cnt == 99:
                cnt = 0

            self.server_db.task()

            time.sleep(1)
            # self.any_signal.emit(cnt)

    def stop(self):
        self.is_running = False
        print('Stopping thread...')
        # cierro conexion
        self.server_db.stop()
        self.terminate()

