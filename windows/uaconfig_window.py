from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
import sys

from modbusTCP_DB.config.ConfigUA import *

from ua_config_window_ui import Ui_UAConfigForm


class UAConfigWindow(QtWidgets.QDialog, Ui_UAConfigForm):
    def __init__(self, db_c: ConfigUA, *args, **kwargs):
        QtWidgets.QDialog.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.config = db_c
        self.update()
        self.save_pushButton.clicked.connect(self.save)
        self.cancel_pushButton.clicked.connect(self.cerrar)

    def cerrar(self):
        self.close()

    def update(self):
        self.endpoint_lineEdit.setText(self.config.conf_ua.endpoint_ua)
        self.uri_lineEdit.setText(self.config.conf_ua.uri)
        self.app_uri_lineEdit.setText(self.config.conf_ua.application_uri)
        self.prod_uri_lineEdit.setText(self.config.conf_ua.product_uri)
        self.name_lineEdit.setText(self.config.conf_ua.name)
        self.man_name_lineEdit.setText(self.config.conf_ua.manufacturer_name)

    def save(self):
        self.config.conf_ua.endpoint_ua = self.endpoint_lineEdit.text()
        self.config.conf_ua.uri = self.uri_lineEdit.text()
        self.config.conf_ua.application_uri = self.app_uri_lineEdit.text()
        self.config.conf_ua.product_uri = self.prod_uri_lineEdit.text()
        self.config.conf_ua.name = self.name_lineEdit.text()
        self.config.conf_ua.manufacturer_name = self.man_name_lineEdit.text()

        ua_conf = dict()
        ua_conf["endpoint_ua"] = self.config.conf_ua.endpoint_ua
        ua_conf["uri"] = self.config.conf_ua.uri
        ua_conf["application_uri"] = self.config.conf_ua.application_uri
        ua_conf["product_uri"] = self.config.conf_ua.product_uri
        ua_conf["name"] = self.config.conf_ua.name
        ua_conf["manufacturer_name"] = self.config.conf_ua.manufacturer_name

        self.config.save(ua_conf)
        self.cerrar()