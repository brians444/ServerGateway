from modbusTCP_DB.modbusTCPService import *
from modbusTCP_DB.modbusRTUService import *
from modbusTCP_DB.OpcUAService import *
from modbusTCP_DB.TimeSeriesDatabase import *

from main_window_ui import Ui_MainWindow
from dbconfig_window import *
from uaconfig_window import *
from mbconfig_window import *
from modbusTCP_DB.Threads import *

from modbusTCP_DB.Threads import *
from var_modbus_window import *

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


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)

        logger.info("Iniciando aplicacion....")

        self.pushButton.clicked.connect(self.cerrar)
        self.configDB_pushButton.clicked.connect(self.openDbConfig)
        self.configUA_pushButton.clicked.connect(self.openUAConfig)
        self.configMB_pushButton.clicked.connect(self.openMbConfig)
        self.var_pushButton.clicked.connect(self.openVarMb)

        self.mb_start_pushButton.clicked.connect(self.startModbusTCP)
        self.mb_stop_pushButton.clicked.connect(self.stopModbusTCP)
        self.mbrtu_start_pushButton.clicked.connect(self.startModbusRTU)
        self.mbrtu_stop_pushButton.clicked.connect(self.stopModbusRTU)

        self.opc_start_pushButton.clicked.connect(self.startOPC)
        self.db_start_pushButton.clicked.connect(self.startDB)
        self.opc_stop_pushButton.clicked.connect(self.stopOPC)
        self.db_stop_pushButton.clicked.connect(self.stopDB)

        self.conf_ua = ConfigUA()
        self.conf_db = ConfigDB()
        self.conf_mb = ConfigMB()

        self.thread = {}
        self.mbrtu_thread = None
        self.db_thread = None
        self.mbtcp_thread = None
        self.opc_thread = None

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


    def cerrar(self):
        self.stopModbusTCP()
        self.stopDB()
        self.stopOPC()
        self.stopModbusRTU()
        self.close()

    def openVarMb(self):
        self.vars_mb_window = VarMbWindow(self.conf_mb)
        self.vars_mb_window.show()


    def setConfig(self, conf: ConfigDB):
        self.config = conf

    def openDbConfig(self):
        self.db_confwindow = DbConfigWindow(self.conf_db)
        self.db_confwindow.show()

    def openUAConfig(self):
        self.ua_confwindow = UAConfigWindow(self.conf_ua)
        self.ua_confwindow.show()

    def openMbConfig(self):
        self.mb_confwindow = MbConfigWindow(self.conf_mb)
        self.mb_confwindow.show()


    def startModbusTCP(self):
        if self.mbtcp_thread is None:
            self.mb_start_pushButton.setEnabled(0)
            self.mb_stop_pushButton.setEnabled(1)
            self.mbtcp_thread = ThreadModbusTCP(services= self.modbusServicesTCP)
            self.mbtcp_thread.start()
            self.mbtcp_servicelabel.setText("Started")
            #self.mb_thread.any_signal.connect(self.my_function)
            #self.pushButton.setEnabled(False)

    def stopModbusTCP(self):
        if self.mbtcp_thread is not None:
            self.mb_start_pushButton.setEnabled(1)
            self.mb_stop_pushButton.setEnabled(0)
            self.mbtcp_thread.stop()
            self.mbtcp_servicelabel.setText("Stopped")
            self.mbtcp_thread = None
            #self.pushButton.setEnabled(True)

    def startModbusRTU(self):
        self.mbrtu_thread = ThreadModbusRTU(services= self.modbusServicesRTU)
        self.mbrtu_thread.start()
        self.mbrtu_servicelabel.setText("Started")
        #self.mb_thread.any_signal.connect(self.my_function)
        #self.pushButton.setEnabled(False)

    def stopModbusRTU(self):
        if self.mbrtu_thread is not None:
            self.mbrtu_thread.stop()
            self.mbrtu_servicelabel.setText("Stopped")
            self.mbrtu_thread = None
        #self.pushButton.setEnabled(True)

    def startOPC(self):
        if self.opc_thread is None:
            self.opc_start_pushButton.setEnabled(0)
            self.opc_stop_pushButton.setEnabled(1)
            self.server_opc = OpcUAService(devices=self.devices, conf_ua=self.conf_ua.conf_ua)
            self.opc_thread = ThreadOPC(opc= self.server_opc)
            self.opc_servicelabel.setText("Started")
            #self.thread[1].any_signal.connect(self.my_function)
        #self.pushButton.setEnabled(False)

    def stopOPC(self):
        if self.opc_thread is not None:
            self.opc_start_pushButton.setEnabled(1)
            self.opc_stop_pushButton.setEnabled(0)
            self.opc_thread.stop()
            self.opc_servicelabel.setText("Stopped")
            self.server_opc = None
            self.opc_thread = None

    def startDB(self):
        if self.db_thread is None:
            self.ts_database = TimeSeriesDatabase(devices=self.devices, db_conf=self.conf_db.db_conf)
            self.db_thread = ThreadDatabase(db=self.ts_database)
            self.db_thread.start()
            self.db_servicelabel.setText("Started")
            #self.thread[1].any_signal.connect(self.my_function)
            #self.pushButton.setEnabled(False)

    def stopDB(self):
        if self.db_thread is not None:
            self.db_thread.stop()
            self.db_servicelabel.setText("Stopped")
            self.ts_database = None
            self.db_thread = None

    def my_function(self, counter):
        cnt = counter
        index = self.sender().index
        if index == 1:
            self.progressBar.setValue(cnt)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())