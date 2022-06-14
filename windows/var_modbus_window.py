import typing

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QApplication,QWidget,QVBoxLayout,QListView,QMessageBox, QInputDialog, QListWidgetItem, QTableWidgetItem
from PyQt5.QtCore import QStringListModel
import sys

from modbusTCP_DB.config.ConfigMB import *

from var_modbus_ui import Ui_VariablesModbus


class VarMbWindow(QtWidgets.QDialog, Ui_VariablesModbus):
    def __init__(self, db_c: ConfigMB, *args, **kwargs):
        QtWidgets.QDialog.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.config = db_c
        self.actualizar_lista_equipos()
        self.close_pushButton.clicked.connect(self.cerrar)
        # Haga clic para activar una función de ranura personalizada
        self.equipos_listView.clicked.connect(self.name_list_clicked)
        self.lecturas_listView.clicked.connect(self.lecturas_list_clicked)

    def cerrar(self):
        self.close()

    def actualizar_lista_equipos(self):
        names = []
        for device in self.config.CONFIG_EQ:
            names.append(device.nombre_equipo)

        # Modelo de lista independiente, agregar datos
        slm = QStringListModel()
        # Establecer vista de lista de modelo, cargar lista de datos
        slm.setStringList(names)
        self.equipos_listView.setModel(slm)

    def name_list_clicked(self, qmodelindex):
        self.cargar_equipo(qmodelindex.row())
        self.actualizar_lista_lecturas()

    def cargar_equipo(self, id: int):
        self.idx = id
        devi = self.config.CONFIG_EQ[self.idx]

    def actualizar_lista_lecturas(self):
        tab_lect = []
        if(self.config.CONFIG_EQ[self.idx].lecturas != None):
            for lect in self.config.CONFIG_EQ[self.idx].lecturas:
                tab_lect.append(lect.file_n)

        # Modelo de lista independiente, agregar datos
        slm2 = QStringListModel()
        # Establecer vista de lista de modelo, cargar lista de datos
        slm2.setStringList(tab_lect)
        self.lecturas_listView.setModel(slm2)

    def lecturas_list_clicked(self, qModelIndex):
        self.idx_lectu = qModelIndex.row()
        vars_lectu = self.config.CONFIG_EQ[self.idx].lecturas[self.idx_lectu]
        self.cargar_lectura(vars_lectu)

    def cargar_lectura(self, vars: ConfigModbusRead):
        self.var_tableWidget.clear()
        self.var_tableWidget.insertColumn(0)
        #self.var_tableWidget.insertRow(0)
        print("Cargando lecturas")
        i = 0
        for var in vars.tabla_nombre_var:
            self.var_tableWidget.insertRow(i)
            i += 1

        self.var_tableWidget.setVerticalHeaderLabels(vars.tabla_nombre_var)
        self.var_tableWidget.setHorizontalHeaderLabels(["Valor"])
        i = 0
        for var in vars.tabla_var:
            print(str(var))
            idDato = QTableWidgetItem(str(var))
            self.var_tableWidget.setItem(i, 0, idDato)

            i += 1




