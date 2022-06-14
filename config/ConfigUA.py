# Config consts
import configparser
import os
import logging

from modbusTCP_DB.config.models import *

logging.getLogger()

CFG_FL_NAME = "config/ua_conf.ini"
DEFAULT_SECTION = "lecturas"


class ConfigUA:  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    def __init__(self):
        # Init config
        self.config_ppal = configparser.ConfigParser()
        # Leo configuracion principal
        self.config_ppal.read(CFG_FL_NAME)

        ua_conf = dict()
        ua_conf["endpoint_ua"] = str(self.config_ppal.get("opc_ua", "end_point"))
        ua_conf["uri"] = str(self.config_ppal.get("opc_ua", "uri"))
        ua_conf["application_uri"] = str(self.config_ppal.get("opc_ua", "application_uri"))
        ua_conf["product_uri"] = str(self.config_ppal.get("opc_ua", "product_uri"))
        ua_conf["name"] = str(self.config_ppal.get("opc_ua", "name"))
        ua_conf["manufacturer_name"] = str(self.config_ppal.get("opc_ua", "manufacturer_name"))

        self.conf_ua = OpcUaConf(ua_conf)

        logging.info("Configuracion leida exitosamente.. ")
        logging.info(f"")

    def save(self, new_conf: dict):
        self.config_ppal.set("opc_ua", "end_point", new_conf["endpoint_ua"])
        self.config_ppal.set("opc_ua", "uri", new_conf["uri"])
        self.config_ppal.set("opc_ua", "application_uri", new_conf["application_uri"])
        self.config_ppal.set("opc_ua", "product_uri", new_conf["product_uri"])
        self.config_ppal.set("opc_ua", "name", new_conf["name"])
        self.config_ppal.set("opc_ua", "manufacturer_name", new_conf["manufacturer_name"])

        with open(CFG_FL_NAME, 'w') as configfile:
            self.config_ppal.write(configfile)
        logging.info("Configuracion guardada exitosamente.. ")