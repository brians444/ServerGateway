from modbusTCP_DB.modbusTCPService import *
from modbusTCP_DB.modbusRTUService import *
from modbusTCP_DB.OpcUAService import *
from modbusTCP_DB.TimeSeriesDatabase import *

from main_window_ui import Ui_MainWindow
from dbconfig_window import *
from uaconfig_window import *
from mbconfig_window import *
from fermentador_window import *
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
        self.vars_mb_window = None
        self.db_confwindow = None
        self.ua_confwindow = None
        self.mb_confwindow = None
        self.ferm1_window = None

        self.pushButton.clicked.connect(self.cerrar)
        self.configDB_pushButton.clicked.connect(self.openDbConfig)
        self.configUA_pushButton.clicked.connect(self.openUAConfig)
        self.configMB_pushButton.clicked.connect(self.openMbConfig)
        self.var_pushButton.clicked.connect(self.openVarMb)
        self.ferm1_pushButton.clicked.connect(self.openferm1)

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

        self.thread = ServiceThread(conf_ua= self.conf_ua, conf_db= self.conf_db, conf_mb=self.conf_mb)
        self.thread.start()

        self.thread.mb_state_signal.connect(self.updateMBState)
        self.thread.db_state_signal.connect(self.updateDBState)
        self.thread.opc_state_signal.connect(self.updateOPCState)
        self.thread.mb_update_signal.connect(self.updateData)

        app.aboutToQuit.connect(self.cerrar)

    def openferm1(self):
        self.ferm1_window = FermentadorWindow(self.thread, 0)
        self.ferm1_window.isEnabled()
        self.ferm1_window.show()

    def updateData(self):
        print("Datos actualizados")
        if self.ferm1_window is not None:
            if self.ferm1_window.isEnabled():
                self.ferm1_window.update_data()

    def cerrar(self):
        self.thread.stop()
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
        self.mb_start_pushButton.setEnabled(0)
        self.mb_stop_pushButton.setEnabled(1)
        self.thread.mbtcp_server_cmd = 1
        self.mbtcp_servicelabel.setText("Starting...")
        #self.thread.any_signal.connect(self.my_function)
        #self.pushButton.setEnabled(False)

    def updateMBState(self, state: int):
        print("Señal recibida actualizando estado Modbus:")
        print(state)
        if (state == 0):
            self.mbtcp_servicelabel.setText("No initiated")
        if (state == 1):
            self.mbtcp_servicelabel.setText("Running...")
        if (state == 2):
            self.mbtcp_servicelabel.setText("Stopped")

    def updateDBState(self, state: int):
        if (state == 0):
            self.db_servicelabel.setText("No initiated")
        if (state == 1):
            self.db_servicelabel.setText("Running...")
        if (state == 2):
            self.db_servicelabel.setText("Stopped")

    def updateOPCState(self, state: int):
        if (state == 0):
            self.opc_servicelabel.setText("No initiated")
        if (state == 1):
            self.opc_servicelabel.setText("Running...")
        if (state == 2):
            self.opc_servicelabel.setText("Stopped")

    def stopModbusTCP(self):
        self.mb_start_pushButton.setEnabled(1)
        self.mb_stop_pushButton.setEnabled(0)
        self.thread.mbtcp_server_cmd = 2
        self.mbtcp_servicelabel.setText("Stoping...")
        #self.pushButton.setEnabled(True)

    def startModbusRTU(self):
        self.mbrtu_servicelabel.setText("Started")
        self.mbrtu_start_pushButton.setEnabled(1)
        self.mbrtu_stop_pushButton.setEnabled(0)
        #self.mb_thread.any_signal.connect(self.my_function)
        #self.pushButton.setEnabled(False)

    def stopModbusRTU(self):
        self.mbrtu_servicelabel.setText("Stopped")
        #self.pushButton.setEnabled(True)

    def startOPC(self):
        self.opc_servicelabel.setText("Started")
        self.thread.opc_server_cmd = 1
        self.opc_start_pushButton.setEnabled(0)
        self.opc_stop_pushButton.setEnabled(1)

    def stopOPC(self):
        self.opc_servicelabel.setText("Stopped")
        self.thread.opc_server_cmd = 2
        self.opc_start_pushButton.setEnabled(1)
        self.opc_stop_pushButton.setEnabled(0)

    def startDB(self):
        self.db_servicelabel.setText("Started")
        self.thread.db_logging_cmd = 1
        self.db_start_pushButton.setEnabled(0)
        self.db_stop_pushButton.setEnabled(1)

    def stopDB(self):
        self.db_servicelabel.setText("Stopped")
        self.thread.db_logging_cmd = 2
        self.db_start_pushButton.setEnabled(1)
        self.db_stop_pushButton.setEnabled(0)

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