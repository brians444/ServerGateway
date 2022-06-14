import logging
import typing

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication,QWidget,QVBoxLayout,QListView,QMessageBox, QInputDialog, QListWidgetItem
from PyQt5.QtCore import QStringListModel
import sys

from modbusTCP_DB.config.ConfigMB import *

from modbus_config_ui import Ui_ModbusConfig


class MbConfigWindow(QtWidgets.QDialog, Ui_ModbusConfig):
    def __init__(self, db_c: ConfigMB, *args, **kwargs):
        QtWidgets.QDialog.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.config = db_c
        self.actualizar_lista_equipos()
        self.close_pushButton.clicked.connect(self.cerrar)
        self.new_eq_pushButton.clicked.connect(self.nuevo_equipo)
        self.new_lect_pushButton.clicked.connect(self.nueva_lectura)
        self.save_eq_pushButton.clicked.connect(self.guardar_equipo)
        self.type_comboBox.currentIndexChanged.connect(self.eq_type_changed)

        # Haga clic para activar una función de ranura personalizada
        self.equipos_listView.clicked.connect(self.name_list_clicked)
        self.lecturas_listView.clicked.connect(self.lecturas_list_clicked)
        #self.numer_reg_spinBox.valueChanged.connect(self.num_variables_cambiado)
        self.numer_reg_spinBox.setDisabled(1)
        #self.equipos_listView.clicked.connect(self.name_list_clicked)
        self.save_lec_pushButton.clicked.connect(self.guardar_lectura)
        self.add_reg_pushButton.clicked.connect(self.add_var_read)
        self.remove_reg_pushButton.clicked.connect(self.del_var_read)
        self.edit_read_pushButton.clicked.connect(self.edit_var_read)
        self.del_lec_pushButton.clicked.connect(self.eliminar_lectura)


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

    def eq_type_changed(self):
        if(self.type_comboBox.currentText() == "TCP"):
            self.label_6.setText("IP - HOST")
            self.label_7.setText("PUERTO (502 default) ")
        else:
            self.label_6.setText("PUERTO")
            self.label_7.setText("BAUDRATE")


    def cargar_equipo(self, id:int):
        self.idx = id
        devi = self.config.CONFIG_EQ[self.idx]
        if devi.type == 'rtu':
            self.name_lineEdit.setText(devi.nombre_equipo)
            self.id_lineEdit.setText(str(devi.id_equipo))
            self.type_comboBox.setCurrentIndex(0) # RTU
            self.port_lineEdit.setText(str(devi.rtu_port))
            self.baud_lineEdit.setText(str(devi.baudrate))
            self.timeout_lineEdit.setText(str(devi.timeout))
        else:
            self.type_comboBox.setCurrentIndex(1)  # TCP
            self.port_lineEdit.setText(devi.ip)
            self.baud_lineEdit.setText(str(devi.port))
            self.name_lineEdit.setText(devi.nombre_equipo)
            self.id_lineEdit.setText(str(devi.id_equipo))
            self.timeout_lineEdit.setText(str(devi.timeout))

    def nuevo_equipo(self):
        text, ok = QInputDialog.getText(self, 'Nuevo equipo', 'Ingrese nombre nuevo equipo')
        if ok:
            self.new_equip_pressed = 1
            ###3 VER ESTO PARA AGREGAR LA NUEVA LECTURA EN MEMORIA.
            n_eq = ConfigModbusDev(nuevo_eq(text))
            self.config.CONFIG_EQ.append(n_eq)
            self.config.N_EQUIPOS = self.config.N_EQUIPOS +1
            self.config.EQUIPOS.append(n_eq.conf_file)
            self.actualizar_lista_equipos()
            self.cargar_equipo(len(self.config.CONFIG_EQ)-1)
            # self.config.CONFIG_EQ[self.idx].lecturas.append()


    def guardar_equipo(self):
        self.new_equip_pressed = 0
        idx = self.equipos_listView.currentIndex().row()
        type_driver = self.type_comboBox.currentText().lower()
        logging.info("Guardando equipo %i tipo : %s", idx, type_driver)

        self.config.CONFIG_EQ[idx].type = type_driver
        self.config.CONFIG_EQ[idx].nombre_equipo = self.name_lineEdit.text()
        #self.config.EQUIPOS[idx].conf_file =
        self.config.CONFIG_EQ[idx].id_equipo = int(self.id_lineEdit.text())
        self.config.CONFIG_EQ[idx].num_lecturas = self.config.CONFIG_EQ[idx].num_lecturas
        logging.info("Guardando equipo %s id : %s", self.name_lineEdit.text(), self.id_lineEdit.text())
        self.config.CONFIG_EQ[idx].bytesize = 8
        self.config.CONFIG_EQ[idx].parity = 0
        self.config.CONFIG_EQ[idx].stopbits = 1

        if(self.endian_comboBox.currentText() == "BIG ENDIAN"):
            self.config.CONFIG_EQ[idx].big_endian = True
        else:
            self.config.CONFIG_EQ[idx].big_endian = False

        self.config.CONFIG_EQ[idx].timeout = float(self.timeout_lineEdit.text())
        if type_driver == "tcp":
            self.config.CONFIG_EQ[idx].port = int(self.baud_lineEdit.text())
            self.config.CONFIG_EQ[idx].ip = self.port_lineEdit.text()
            self.config.CONFIG_EQ[idx].baudrate = 0
            self.config.CONFIG_EQ[idx].rtu_port = "null"
        else:
            self.config.CONFIG_EQ[idx].baudrate = int(self.baud_lineEdit.text())
            self.config.CONFIG_EQ[idx].rtu_port = self.port_lineEdit.text()
            self.config.CONFIG_EQ[idx].port = 0
            self.config.CONFIG_EQ[idx].ip = "null"

        self.config.save()

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

    def cargar_lectura(self, vars_lectu: ConfigModbusRead):
        self.vars_listWidget.clear()
        # Cargo primero las variables
        self.vars_listWidget.addItems(vars_lectu.tabla_nombre_var)
        # Cargo despues el numero de variables para evitar el agregado de variables
        self.numer_reg_spinBox.setValue(int(vars_lectu.read_len))
        self.direccion_lect_lineEdit.setText(str(vars_lectu.address))
        self.table_name_lineEdit.setText(str(vars_lectu.file_n))

    def limpiar_lectura(self):
        self.vars_listWidget.clear()
        self.numer_reg_spinBox.setValue(int(0))
        self.direccion_lect_lineEdit.setText(str(30001))
        self.table_name_lineEdit.setText(str(""))

    def nueva_lectura(self):
        text, ok = QInputDialog.getText(self, 'Nombre tabla variables', 'Ingrese el archivo de lecturas')
        if ok:
            if(self.idx >= 0):
                n_lec = ConfigModbusRead(nuevo_read(text))
                self.config.CONFIG_EQ[self.idx].lecturas.append(n_lec)
                self.config.CONFIG_EQ[self.idx].num_lecturas += 1
                self.actualizar_lista_lecturas()
                self.cargar_lectura(n_lec)
                self.idx_lectu = self.lecturas_listView.model().rowCount()-1
            else:
                QMessageBox.information(self, 'Debe seleccionar un equipo')

    def eliminar_lectura(self):
        sel_lectur = self.config.CONFIG_EQ[self.idx].lecturas[self.idx_lectu]
        self.config.CONFIG_EQ[self.idx].lecturas.remove(sel_lectur)
        self.config.CONFIG_EQ[self.idx].num_lecturas -= 1
        self.idx_lectu = self.lecturas_listView.model().rowCount() - 1
        self.actualizar_lista_lecturas()
        self.limpiar_lectura()

    def guardar_lectura(self):
        names_vars = []
        c = self.vars_listWidget.count()
        if c > 0:
            for item in range(c):
                print(self.vars_listWidget.item(item).text())
                names_vars.append(self.vars_listWidget.item(item).text())

            self.config.CONFIG_EQ[self.idx].lecturas[self.idx_lectu].tabla_nombre_var = names_vars
            self.config.CONFIG_EQ[self.idx].lecturas[self.idx_lectu].read_len = int(self.numer_reg_spinBox.value())
            self.config.CONFIG_EQ[self.idx].lecturas[self.idx_lectu].address = int(self.direccion_lect_lineEdit.text())
            self.config.CONFIG_EQ[self.idx].lecturas[self.idx_lectu].file_n = self.table_name_lineEdit.text()
            self.config.CONFIG_EQ[self.idx].lecturas[self.idx_lectu].type = self.type_comboBox.currentText()

        self.config.save_reads(self.idx)

    # Se usaba para el Spin Box pero lo desactivamos
    def num_variables_cambiado(self):
        num_var = self.numer_reg_spinBox.value()
        cant = self.vars_listWidget.count()
        if cant > num_var :
            #Elimino un item
            self.del_var_read()
        elif cant < num_var:
            self.add_var_read()
        else:
            # no hago nada
            return

    def add_var_read(self):
        text, ok = QInputDialog.getText(self, 'Nombre nueva variable', 'Nombre de la nueva variable')
        if ok:
            num_var = self.numer_reg_spinBox.value()
            actual_item = self.vars_listWidget.currentRow()

            self.numer_reg_spinBox.setValue(num_var+1)
            self.vars_listWidget.insertItem(actual_item+1, text)
            #self.vars_listWidget.addItem(text)

    def del_var_read(self):
        cant = self.vars_listWidget.count()
        if cant > 0:
            row = self.vars_listWidget.currentRow()
            self.vars_listWidget.takeItem(row)
            num_var = self.numer_reg_spinBox.value()
            self.numer_reg_spinBox.setValue(num_var - 1)

    def edit_var_read(self):
        item = self.vars_listWidget.currentItem()
        text, ok = QInputDialog.getText(self, 'Nombre nueva variable', 'Nombre de la nueva variable', text=item.text())
        if ok:
            item.setText(text)
            self.vars_listWidget.editItem(item)


def nuevo_read(tabla:str):
    config_dict = dict()
    config_dict['read_len'] = 1
    config_dict['address'] = 30001
    config_dict['type'] = 'INT16'  # INT16 - UINT16 - INT32 - UINT32 - FLOAT - SWAP FLOAT - DWORD
    config_dict['nombres'] = ['variable1']
    config_dict['register_type'] = 'H'
    config_dict['base_address'] = 30000
    config_dict['nombre_tabla'] = tabla
    return config_dict

def nuevo_eq(nombre:str):
    config_dict = dict()
    config_dict['type'] = 'rtu'
    config_dict['nombre_equipo'] = nombre
    config_dict['conf_file'] = 'config/' + nombre + '.ini'
    config_dict['id_equipo'] = 1
    config_dict['num_lecturas'] = 0
    config_dict['bytesize'] = 8
    config_dict['parity'] = 0
    config_dict['stopbits'] = 1
    config_dict['baudrate'] = 9600
    config_dict['rtu_port'] = 'COM1'
    config_dict['timeout'] = 1.0
    config_dict['big_endian'] = 'True'
    config_dict['lecturas']:typing.List[ConfigModbusRead] = []
    return config_dict