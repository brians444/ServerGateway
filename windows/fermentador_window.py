from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QApplication,QWidget,QVBoxLayout,QListView,QMessageBox, QInputDialog, QListWidgetItem
import sys

from modbusTCP_DB.config.ConfigDB import *
from modbusTCP_DB.Threads import *

from fermentador_window_ui import Ui_FermentadorWindow


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt


class FermentadorWindow(QtWidgets.QDialog, Ui_FermentadorWindow):
    def __init__(self, service: ServiceThread, idx: int, *args, **kwargs):
        QtWidgets.QDialog.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.service = service
        self.idx = idx
        self.load_data(idx)
        #self.update()
        #self.save_pushButton.clicked.connect(self.save)
        self.change_high_pushButton.clicked.connect(self.write_high_set)
        self.change_low_pushButton.clicked.connect(self.write_low_set)

        # Plot
        self.figure_timeseries = plt.figure()
        self.canvas_timeseries = FigureCanvas(self.figure_timeseries)
        self.verticalLayout_3.addWidget(self.canvas_timeseries)

        self.timespan = 600
        self.temp1_log = [0.0] * self.timespan
        self.temp2_log = [0.0] * self.timespan
        self.humedad_log = [0.0] * self.timespan

    def update_data(self):
        self.load_data(self.idx)
        self.update_chart_timeseries()


    def load_data(self, idx):
        for lectura in self.service.devices[idx].lecturas:
            i = 0
            self.temp = 0.0
            self.high_set = 0.0
            self.low_set = 0.0
            self.amb_temp = 0.0
            self.humedad = 0.0
            for var in lectura.tabla_nombre_var:
                if var == "Temperature":
                    self.temp = lectura.tabla_var[i]
                elif var == "Setpoint_high_address":
                    self.high_set = lectura.tabla_var[i]
                elif var == "Setpoint_low_address":
                    self.low_set = lectura.tabla_var[i]
                elif var == "Ambient_Temperature":
                    self.amb_temp = lectura.tabla_var[i]
                elif var == "Humidity":
                    self.humedad = lectura.tabla_var[i]

                i += 1

        self.temp_doubleSpinBox.setValue(float(self.temp))
        self.high_doubleSpinBox.setValue(float(self.high_set))
        self.low_doubleSpinBox.setValue(float(self.low_set))
        self.temp_amb_doubleSpinBox.setValue(float(self.amb_temp))
        self.humidity_doubleSpinBox.setValue(float(self.humedad))

    def update_chart_timeseries(self):  # time series
        self.temp1_log.pop(0)
        self.temp1_log.append(self.temp)
        self.temp2_log.pop(0)
        self.temp2_log.append(self.amb_temp)
        self.humedad_log.pop(0)
        self.humedad_log.append(self.humedad)

        self.figure_timeseries.clear()  #
        plt.figure(num=self.figure_timeseries.number)  #
        plt.plot(self.temp1_log, color="b")
        plt.plot(self.temp2_log, color="r")
        plt.plot(self.humedad_log, color="g")
        #plt.ylim([0,max(self.temp1_log)])
        #plt.title(f'Fermentador %i',self.idx+1)
        plt.ylim(ymin=0)
        plt.grid(True)
        plt.legend(['Temperatura', 'Temp. Ambiente', 'Humedad'], loc='upper left')
        self.canvas_timeseries.draw()

    def write_low_set(self):
        logging.info("Escribiendo setpoint low")
        value, ok = QInputDialog.getDouble(self, 'Set point LOW', 'Nombre de la nueva variable')
        if ok:
            self.service.write_float_reg("Setpoint_low_address", value, self.idx)

    def write_high_set(self):
        logging.info("Escribiendo setpoint high")
        value, ok = QInputDialog.getDouble(self, 'Set point High', 'Nombre de la nueva variable')
        if ok:
            self.service.write_float_reg("Setpoint_high_address", value, self.idx)