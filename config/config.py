# Config consts
# Config consts
import configparser
import os
import logging

from models import *

logging.getLogger()


CFG_FL_NAME = "user.ini"
DEFAULT_SECTION = "lecturas"


class Config:  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    def __init__(self):
        # Init config
        config_ppal = configparser.ConfigParser()
        # Leo configuracion principal
        config_ppal.read(CFG_FL_NAME)

        ua_conf = dict()
        ua_conf["endpoint_ua"] = str(config_ppal.get("opc_ua", "end_point"))
        ua_conf["uri"] = str(config_ppal.get("opc_ua", "uri"))
        ua_conf["application_uri"] = str(config_ppal.get("opc_ua", "application_uri"))
        ua_conf["product_uri"] = str(config_ppal.get("opc_ua", "product_uri"))
        ua_conf["name"] = str(config_ppal.get("opc_ua", "name"))
        ua_conf["manufacturer_name"] = str(config_ppal.get("opc_ua", "manufacturer_name"))

        self.conf_ua = OpcUaConf(ua_conf)

        ## DATABASE CONFIG
        db_conf = dict()
        db_conf["bucket"] = str(config_ppal.get("database", "bucket"))
        db_conf["org"] = str(config_ppal.get("database", "org"))
        db_conf["token"] = str(config_ppal.get("database", "token"))
        db_conf["ip"] = str(config_ppal.get("database", "url"))
        db_conf["port"] = str(config_ppal.get("database", "port"))
        db_conf["url"] = db_conf["ip"]+":"+db_conf["port"]
        db_conf["name"] = str(config_ppal.get("database", "name"))

        self.db_conf = DatabaseConfig(db_config=db_conf)
        ## END DATABASE CONFIG



        self.N_EQUIPOS = int(config_ppal.get("equipos", "numero_equipos"))
        self.EQUIPOS = []
        for i in range(self.N_EQUIPOS):
            file_equipo = "equipo_"+str(i+1)
            file_equipo = config_ppal.get("equipos", file_equipo)
            if os.path.exists(file_equipo):
                self.EQUIPOS.append(file_equipo)
            else:
                logging.error(f"Error el archivo de configuracion  no existe: %s", file_equipo)

        logging.info(f"Leyendo configuracion..")
        logging.info(f"Cantidad de equipos %i - lista de archivos: %s", self.N_EQUIPOS, self.EQUIPOS)

        self.CONFIG_EQ = []

        for equipo in self.EQUIPOS:
            conf_eq = dict()
            # Init config
            config = configparser.ConfigParser()
            # Leo configuracion principal
            if os.path.exists(equipo):
                config.read(equipo)
            else:
                logging.error(f"Error Abriendo archivo de configuracion : %s", equipo)
                break

            id_equipo = config.get(DEFAULT_SECTION, "id_modbus")
            nombre_equipo = config.get(DEFAULT_SECTION, "nombre")
            try:
                big_end = config.get(DEFAULT_SECTION, "big_endian")
            except:
                big_end = "TRUE"
                logging.error("Big endian no se encontro en la configuracion. Usando TRUE por defecto..")

            try:
                timeout = config.get(DEFAULT_SECTION, "timeout")
            except:
                timeout = 1000
                logging.error("Timeout no se encontro en la configuracion. Usando 1000ms por defecto..")

            num_lecturas = int(config.get(DEFAULT_SECTION, "numero_lecturas"))

            type = config.get(DEFAULT_SECTION, "type")
            if type == "tcp":
                ip = config.get(DEFAULT_SECTION, "ip")
                try:
                    puerto = int(config.get(DEFAULT_SECTION, "puerto_tcp"))
                except:
                    puerto = 502
                    logging.error("Puerto TCP no se encontro en la configuracion. Usando 502 por defecto..")
                conf_eq["ip"] = ip
                conf_eq['port'] = puerto
            else:
                rtu_port = config.get(DEFAULT_SECTION, "rtu_port")
                try:
                    baudrate = int(config.get(DEFAULT_SECTION, "baudrate"))
                except:
                    baudrate = 9600
                    logging.error("Baudrate no se encontro en la configuracion. Usando 9600 por defecto..")
                conf_eq["rtu_port"] = rtu_port
                conf_eq["baudrate"] = baudrate

            conf_eq["type"] = type
            conf_eq["nombre_equipo"] = nombre_equipo
            conf_eq["conf_file"] = equipo
            conf_eq["id_equipo"] = id_equipo
            conf_eq["num_lecturas"] = num_lecturas
            conf_eq["big_endian"] = big_end
            conf_eq['timeout'] = timeout


            lecturas = []
            for i in range(num_lecturas):
                nombre = "lectura_"+str(i+1)
                lenght = int(config.get(nombre, "len"))
                type_var = config.get(nombre, "type")
                address = int(config.get(nombre, "address"))
                nombre = config.get(nombre, "tabla")


                if address >= 40000 and address < 50000:
                    register = "I"      # INPUT REGISTER (0x04)
                    base_address = address - 40000
                elif address >= 30000:
                    register = "H"      # HOLDING REGISTER (0x03)
                    base_address = address - 30000
                elif address >= 20000:
                    register = "D"      # DISCRETE INPUT REGISTER
                    base_address = address - 20000
                else:
                    register = "C"      # COIL REGISTER
                    base_address = address - 10000


                nombres = []
                # Get lecturas from lectura_X file
                if os.path.exists(nombre):
                    with open(nombre) as rfh:
                        for line in rfh:
                            line = line.strip()
                            if not line or line.startswith("#") or line in nombres:
                                continue
                            nombres.append(line)
                if len(nombres) != lenght:
                    logging.error(f"ERROR en lectura %i La cantidad de nombres se debe corresponder con la longitud de la lectura", i+1)

                lectura = dict()
                lectura['read_len'] = lenght
                lectura['address'] = address
                lectura['type'] = type_var
                lectura['nombres'] = nombres
                lectura['register_type'] = register
                lectura['base_address'] = base_address

                lectura = ConfigModbusRead(lectura)
                lecturas.append(lectura)

            conf_eq["lecturas"] = lecturas
            dev_nuevo = ConfigModbusDev(conf_eq)
            self.CONFIG_EQ.append(dev_nuevo)

        logging.info(f"Config leida:")
        for eq in self.CONFIG_EQ:
            if type == "tcp":
                logging.info(f"Nombre de equipo: %s - ConfigFile:%s - IP= %s, PUERTO= %i ID= %s BIG_ENDIAN= %s", eq.nombre_equipo, eq.conf_file, eq.ip, eq.port, eq.id_equipo, str(eq.big_endian))
            if type == "rtu":
                logging.info(f"Nombre de equipo: %s - ConfigFile:%s - PUERTO= %s, BAUDRATE= %i ID= %s BIG_ENDIAN= %s",
                             eq.nombre_equipo, eq.conf_file, eq.rtu_port, eq.baudrate, eq.id_equipo, str(eq.big_endian))
            for lectura in eq.lecturas:
                logging.info(f" len= %i - address= %s - tipo= %s -  nombres: %s", lectura.read_len, lectura.address, lectura.type, lectura.tabla_nombre_var)

        logging.info("Configuracion leida exitosamente.. ")
        logging.info(f"")

