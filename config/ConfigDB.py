
# Config consts
import configparser
import os
import logging

from modbusTCP_DB.config.models import *

logging.getLogger()

CFG_FL_NAME = "config/db_conf.ini"
DEFAULT_SECTION = "lecturas"


class ConfigDB:  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    def __init__(self):
        # Init config
        self.config_ppal = configparser.ConfigParser()
        # Leo configuracion principal
        self.config_ppal.read(CFG_FL_NAME)

        ## DATABASE CONFIG
        db_conf = dict()
        db_conf["bucket"] = str(self.config_ppal.get("database", "bucket"))
        db_conf["org"] = str(self.config_ppal.get("database", "org"))
        db_conf["token"] = str(self.config_ppal.get("database", "token"))
        db_conf["ip"] = str(self.config_ppal.get("database", "url"))
        db_conf["port"] = str(self.config_ppal.get("database", "port"))
        db_conf["url"] = db_conf["ip"] + ":" + db_conf["port"]
        db_conf["name"] = str(self.config_ppal.get("database", "name"))

        self.db_conf = DatabaseConfig(db_config=db_conf)

        logging.info("Configuracion leida exitosamente.. ")
        logging.info(f"")

    def save(self, new_conf: dict):
        self.config_ppal.set("database", "bucket", new_conf["bucket"])
        self.config_ppal.set("database", "org", new_conf["org"])
        self.config_ppal.set("database", "token", new_conf["token"])
        self.config_ppal.set("database", "url", new_conf["url"]) # Guardo solo la IP
        self.config_ppal.set("database", "port", new_conf["port"])
        self.config_ppal.set("database", "name", new_conf["name"])

        with open(CFG_FL_NAME, 'w') as configfile:
            self.config_ppal.write(configfile)
        logging.info("Configuracion guardada exitosamente.. ")

"""
# instantiate
config = ConfigParser()

# parse existing file
config.read('test.ini')

# read values from a section
string_val = config.get('section_a', 'string_val')
bool_val = config.getboolean('section_a', 'bool_val')
int_val = config.getint('section_a', 'int_val')
float_val = config.getfloat('section_a', 'pi_val')

# update existing value
config.set('section_a', 'string_val', 'world')

# add a new section and some values
config.add_section('section_b')
config.set('section_b', 'meal_val', 'spam')
config.set('section_b', 'not_found_val', '404')

# save to a file
with open('test_update.ini', 'w') as configfile:
    config.write(configfile)

"""