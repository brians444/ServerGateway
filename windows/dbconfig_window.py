from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
import sys

from modbusTCP_DB.config.ConfigDB import *

from db_config_window_ui import Ui_DBConfigForm


class DbConfigWindow(QtWidgets.QDialog, Ui_DBConfigForm):
    def __init__(self, db_c: ConfigDB, *args, **kwargs):
        QtWidgets.QDialog.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.config = db_c
        self.update()
        self.save_pushButton.clicked.connect(self.save)

    def cerrar(self):
        self.close()

    def update(self):
        self.url_lineEdit.setText(self.config.db_conf.url.split(":")[0])
        self.port_lineEdit.setText(self.config.db_conf.port)
        self.token_lineEdit.setText(self.config.db_conf.token)
        self.bucket_lineEdit.setText(self.config.db_conf.bucket)
        self.name_lineEdit.setText(self.config.db_conf.name)
        self.org_lineEdit.setText(self.config.db_conf.org)

    def save(self):
        self.config.db_conf.url = self.url_lineEdit.text() + ":" + self.port_lineEdit.text()
        self.config.db_conf.port = self.port_lineEdit.text()
        self.config.db_conf.token = self.token_lineEdit.text()
        self.config.db_conf.bucket = self.bucket_lineEdit.text()
        self.config.db_conf.name = self.name_lineEdit.text()
        self.config.db_conf.org = self.org_lineEdit.text()

        db_conf = dict()
        db_conf["bucket"] = self.config.db_conf.bucket
        db_conf["org"] = self.config.db_conf.org
        db_conf["token"] = self.config.db_conf.token
        db_conf["ip"] = str(self.url_lineEdit.text())
        db_conf["port"] = str(self.config.db_conf.port)
        db_conf["url"] = db_conf["ip"] + ":" + db_conf["port"]
        db_conf["name"] = self.config.db_conf.name
        self.config.save(db_conf)
        self.close()