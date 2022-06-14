import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

import logging
import typing
logging.getLogger()

from modbusTCP_DB.config.models import *


class TimeSeriesDatabase:
    def __init__(self, devices: typing.List[ConfigModbusDev], db_conf: DatabaseConfig):
        self.config = db_conf

        logging.info("Instanciando Time Series Database")
        logging.info(f"URL : %s ", self.config.url)
        logging.info(f"bucket : %s , org: %s ", self.config.bucket, self.config.org)
        self.client = influxdb_client.InfluxDBClient(
            url=self.config.url,
            token=self.config.token,
            org=self.config.org
        )

        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

        self.devices = devices
        self.objectos_eq = dict()
        self.devices = []

        # populating our address space
        for dev in devices:
            self.devices.append(TimeSeriesDevice(device=dev, write_api=self.write_api))

        # Inicio el servidor
        self.start()

    def task(self):
        write_list = []
        for dev in self.devices:
            dev.update()
            write_list.append(dev.write_list)

        for point in write_list:
            try:
                self.write_api.write(bucket=self.config.bucket, org=self.config.org, record=point)
            except:
                logging.error(f"error adding poing to influx db : %s",point)

    def start(self):
        logging.info("CLient Influx DB iniciado - Haciendo ping")
        self.client.ping()

    def stop(self):
        self.client.close()



class TimeSeriesDevice:
    def __init__(self, device: ConfigModbusDev, write_api):
        self.device = device
        self.write_api = write_api

        self.nombre = self.device.nombre_equipo

        self.variables = dict()

        self.write_list = []

        for lecture in self.device.lecturas:
            for i in range(len(lecture.tabla_nombre_var)):
                p = influxdb_client.Point("my_measurements").tag("device", self.device.nombre_equipo).field(lecture.tabla_nombre_var[i], lecture.tabla_var[i])
                self.write_list.append(p)


        # populating our address space
         #   for k, v in dev.lecturas:
         #       self.variables.append(self.objectos_eq[dev.nombre_equipo].add_variable(self.idx, , v))


    def update(self):
        self.write_list = []
        for lecture in self.device.lecturas:
            for i in range(len(lecture.tabla_nombre_var)):
                p = influxdb_client.Point("my_measurements").tag("device", self.device.nombre_equipo).field(
                    lecture.tabla_nombre_var[i], lecture.tabla_var[i])
                self.write_list.append(p)


