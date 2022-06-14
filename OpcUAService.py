import os

from opcua import Server

import logging
import typing
from modbusTCP_DB.config.models import *

logging.getLogger()


class OpcUAService:
    def __init__(self, devices: typing.List[ConfigModbusDev], conf_ua: OpcUaConf):
        self.config = conf_ua

        self.devices = devices
        self.endpoint = self.config.endpoint_ua
        self.server = Server()
        #self.server.
        #self.server.set_endpoint(self.endpoint)
        self.server.set_application_uri(self.config.application_uri)
        self.server.set_server_name(self.config.name)
        self.server.manufacturer_name = self.config.manufacturer_name
        self.server.set_endpoint(self.endpoint)
        #self.server.set_endpoint("opc.tcp://0.0.0.0:4870/server/")

        logging.info("Instanciando servidor UA")
        logging.info(f"Endpoint : %s ", self.endpoint)


        # load server certificate and private key. This enables endpoints
        # with signing and encryption.

        if os.path.exists("modbusPY.der"):
            logging.info("Loading certificate")
            self.server.load_certificate("modbusPY.der")
        #if os.path.exists("modbusPY.pem"):
            #logging.info("Loading private key")
            #self.server.load_private_key("modbusPY.pem")

        self.uri = self.config.uri
        self.idx = self.server.register_namespace(self.uri)

        logging.info(f"URI : %s ", self.uri)

        # get Objects node, this is where we should put our nodes
        self.objects = self.server.get_objects_node()

        self.objectos_eq = dict()
        self.equipos_ua = []

        # populating our address space
        for dev in devices:
            #self.objectos_eq[dev.nombre_equipo] = OpcUADevice(device=dev)
            self.equipos_ua.append(OpcUADevice(device=dev, namespace=self.idx, object_node=self.objects))

        # Inicio el servidor
        self.start()

    def task(self):
        for opc_dev in self.equipos_ua:
            opc_dev.update()

    def start(self):
        logging.info("Iniciando servidor OPC UA")
        self.server.start()

    def stop(self):
        self.server.stop()



class OpcUADevice:
    def __init__(self, device: ConfigModbusDev, namespace, object_node):
        self.device = device
        self.idx = namespace
        self.objects = object_node

        self.objecto_eq = self.objects.add_object(self.idx, self.device.nombre_equipo)

        self.variables = dict()

        for lecture in self.device.lecturas:
            for i in range(len(lecture.tabla_nombre_var)):
                self.variables[lecture.tabla_nombre_var[i]] = self.objecto_eq.add_variable(self.idx, lecture.tabla_nombre_var[i], lecture.tabla_var[i])


        # populating our address space
         #   for k, v in dev.lecturas:
         #       self.variables.append(self.objectos_eq[dev.nombre_equipo].add_variable(self.idx, , v))


    def update(self):
        for lecture in self.device.lecturas:
            for i in range(len(lecture.tabla_nombre_var)):
                self.variables[lecture.tabla_nombre_var[i]].set_value(lecture.tabla_var[i])
        #self.error_var.set_value(self.error)
        #self.variables[index].set_value(item[nombres[i]])

