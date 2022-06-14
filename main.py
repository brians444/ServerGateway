from modbusTCPService import *
from modbusRTUService import *
from OpcUAService import *
from TimeSeriesDatabase import *

import time

from config.ConfigUA import *
from config.ConfigDB import *
from config.ConfigMB import *

logger = logging.getLogger()

logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s :: %(message)s')
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler('info.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

if __name__ == "__main__":
    try:
        logger.info("Iniciando aplicacion....")
        conf_ua = ConfigUA()
        conf_db = ConfigDB()
        conf_mb = ConfigMB()

        modbusServices = []
        devices = []
        for device in conf_mb.CONFIG_EQ:
            if(device.type == 'rtu'):
                modbusServices.append(ModbusRTUService(dev_modbus=device))
            else:
                modbusServices.append(ModbusTCPService(dev_modbus=device))

            devices.append(device)

        server_opc = OpcUAService(devices, conf_ua=conf_ua.conf_ua)
        ts_database = TimeSeriesDatabase(devices=devices, db_conf=conf_db.db_conf)


        try:
            count = 0
            while True:
                time.sleep(10)
                for service in modbusServices:
                    service.update()

                server_opc.task()
                ts_database.task()

        finally:
            # cierro conexion
            server_opc.stop()
            ts_database.stop()


    except KeyboardInterrupt:
        pass
