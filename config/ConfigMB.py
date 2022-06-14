
# Config consts
import configparser
import os
import logging

from modbusTCP_DB.config.models import *

logging.getLogger()

CFG_FL_NAME = "config/mb_conf.ini"
DEFAULT_SECTION = "lecturas"


class ConfigMB:  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    def __init__(self):
        # Init config
        self.config_ppal = configparser.ConfigParser()
        # Leo configuracion principal
        self.config_ppal.read(CFG_FL_NAME)


        self.N_EQUIPOS = int(self.config_ppal.get("equipos", "numero_equipos"))
        self.EQUIPOS = []
        for i in range(self.N_EQUIPOS):
            file_equipo = "equipo_" + str(i+1)
            file_equipo = self.config_ppal.get("equipos", file_equipo)
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
            self.config = configparser.ConfigParser()
            # Leo configuracion principal
            if os.path.exists(equipo):
                self.config.read(equipo)
            else:
                logging.error(f"Error Abriendo archivo de configuracion : %s", equipo)
                break

            id_equipo = self.config.get(DEFAULT_SECTION, "id_modbus")
            nombre_equipo = self.config.get(DEFAULT_SECTION, "nombre")
            try:
                big_end = self.config.get(DEFAULT_SECTION, "big_endian")
            except:
                big_end = "TRUE"
                logging.error("Big endian no se encontro en la configuracion. Usando TRUE por defecto..")

            try:
                timeout = self.config.get(DEFAULT_SECTION, "timeout")
            except:
                timeout = 1000
                logging.error("Timeout no se encontro en la configuracion. Usando 1000ms por defecto..")

            num_lecturas = int(self.config.get(DEFAULT_SECTION, "numero_lecturas"))

            type = self.config.get(DEFAULT_SECTION, "type")
            if type == "tcp":
                ip = self.config.get(DEFAULT_SECTION, "ip")
                try:
                    puerto = int(self.config.get(DEFAULT_SECTION, "puerto_tcp"))
                except:
                    puerto = 502
                    logging.error("Puerto TCP no se encontro en la configuracion. Usando 502 por defecto..")
                conf_eq["ip"] = ip
                conf_eq['port'] = puerto
            else:
                rtu_port = self.config.get(DEFAULT_SECTION, "rtu_port")
                try:
                    baudrate = int(self.config.get(DEFAULT_SECTION, "baudrate"))
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
                nombre = "lectura_" +str(i+1)
                lenght = int(self.config.get(nombre, "len"))
                type_var = self.config.get(nombre, "type")
                address = int(self.config.get(nombre, "address"))
                nombre_tabla = self.config.get(nombre, "tabla")


                if address >= 40000 and address < 50000:
                    register = "H"      # INPUT REGISTER (0x04)
                    base_address = address - 40000
                elif address >= 30000:
                    register = "I"      # HOLDING REGISTER (0x03)
                    base_address = address - 30000
                elif address >= 20000:
                    register = "D"      # DISCRETE INPUT REGISTER
                    base_address = address - 20000
                else:
                    register = "C"      # COIL REGISTER
                    base_address = address - 10000


                nombres = []
                # Get lecturas from lectura_X file
                if os.path.exists(nombre_tabla):
                    with open(nombre_tabla) as rfh:
                        for line in rfh:
                            line = line.strip()
                            if not line or line.startswith("#") or line in nombres:
                                continue
                            nombres.append(line)
                if len(nombres) != lenght:
                    logging.error(f"ERROR en lectura %i La cantidad de nombres se debe corresponder con la longitud de la lectura %i != %i ", i+ 1, len(nombres), lenght)

                lectura = dict()
                lectura['read_len'] = lenght
                lectura['address'] = address
                lectura['type'] = type_var
                lectura['nombres'] = nombres
                lectura['register_type'] = register
                lectura['base_address'] = base_address
                lectura['nombre_tabla'] = str(nombre_tabla)

                lectura = ConfigModbusRead(lectura)
                lecturas.append(lectura)

            conf_eq["lecturas"] = lecturas
            dev_nuevo = ConfigModbusDev(conf_eq)
            self.CONFIG_EQ.append(dev_nuevo)

        logging.info(f"Config leida:")
        for eq in self.CONFIG_EQ:
            if type == "tcp":
                logging.info(f"Nombre de equipo: %s - ConfigFile:%s - IP= %s, PUERTO= %i ID= %s BIG_ENDIAN= %s",
                             eq.nombre_equipo, eq.conf_file, eq.ip, eq.port, eq.id_equipo, str(eq.big_endian))
            if type == "rtu":
                logging.info(f"Nombre de equipo: %s - ConfigFile:%s - PUERTO= %s, BAUDRATE= %i ID= %s BIG_ENDIAN= %s",
                             eq.nombre_equipo, eq.conf_file, eq.rtu_port, eq.baudrate, eq.id_equipo, str(eq.big_endian))
            for lectura in eq.lecturas:
                logging.info(f" len= %i - address= %s - tipo= %s -  nombres: %s", lectura.read_len, lectura.address,
                             lectura.type, lectura.tabla_nombre_var)

        logging.info("Configuracion leida exitosamente.. ")
        logging.info(f"")

    def save(self):
        print("Saving...")
        self.save_devices()

    # Guardo lecturas
    def save_reads(self, idx: int):
        logging.info("Guardando lecturas")
        equipo = self.CONFIG_EQ[idx]
        config = configparser.ConfigParser()
        if os.path.exists(equipo.conf_file):
            config.read(equipo.conf_file)

        config.set(DEFAULT_SECTION, "numero_lecturas", str(equipo.num_lecturas))
        i = 1
        for lectura in equipo.lecturas:
            print("Seccion: ")
            seccion = "lectura_"+str(i)
            print(seccion)
            try:
                config.add_section(seccion)
            except:
                print("La seccion ya existe")

            config.set(seccion, "tabla", lectura.file_n)
            config.set(seccion, "address", str(lectura.address))
            config.set(seccion, "len", str(lectura.read_len))
            config.set(seccion, "type", str(lectura.type))

            f = open(lectura.file_n, "w")
            for linea in lectura.tabla_nombre_var:
                f.write(linea+'\n')
            f.close()

        with open(equipo.conf_file, 'w') as configfile:
            config.write(configfile)



    def save_devices(self):
        print("Saving dev")
        config_ppal = configparser.ConfigParser()
        config_ppal.add_section("equipos")
        n_equipos = self.N_EQUIPOS
        print(n_equipos)
        config_ppal.set("equipos", "numero_equipos", str(n_equipos))
        i = 0

        for equipo in self.CONFIG_EQ:
            print("Saving dev - ")
            print(equipo.conf_file)
            logging.error(f"Guardando Dispositivo %s , fichero = %s", equipo.nombre_equipo, equipo.conf_file)
            file_equipo = "equipo_" + str(i + 1)
            config_ppal.set("equipos", file_equipo, equipo.conf_file)

            # Guardo config principal
            config = configparser.ConfigParser()
            config.add_section(DEFAULT_SECTION)

            config.set(DEFAULT_SECTION, "id_modbus", str(equipo.id_equipo))
            config.set(DEFAULT_SECTION, "nombre", equipo.nombre_equipo)
            config.set(DEFAULT_SECTION, "timeout", str(int(equipo.timeout*1000)))
            config.set(DEFAULT_SECTION, "big_endian", str(equipo.big_endian))
            config.set(DEFAULT_SECTION, "numero_lecturas", str(equipo.num_lecturas))
            config.set(DEFAULT_SECTION, "type", equipo.type)

            config.set(DEFAULT_SECTION, "bytesize", str(equipo.bytesize))
            config.set(DEFAULT_SECTION, "parity", str(equipo.parity))
            config.set(DEFAULT_SECTION, "stopbits", str(equipo.stopbits))
            if equipo.type == "tcp":
                config.set(DEFAULT_SECTION, "ip", equipo.ip)
                config.set(DEFAULT_SECTION, "puerto_tcp", str(equipo.port))
            else:
                config.set(DEFAULT_SECTION, "rtu_port", equipo.rtu_port)
                config.set(DEFAULT_SECTION, "baudrate", str(equipo.baudrate))
            print(equipo.conf_file)
            with open(equipo.conf_file, 'w') as configfile:
                config.write(configfile)

            self.save_reads(i)
            i = i + 1

        with open(CFG_FL_NAME, 'w') as configfile:
            config_ppal.write(configfile)
        logging.info("Configuracion guardada exitosamente.. ")




        """

        logging.info(f"Leyendo configuracion..")
        logging.info(f"Cantidad de equipos %i - lista de archivos: %s", self.N_EQUIPOS, self.EQUIPOS)

        self.CONFIG_EQ = []

        for equipo in self.EQUIPOS:

            if type == "tcp":
                ip = self.config.get(DEFAULT_SECTION, "ip")
                puerto = int(self.config.get(DEFAULT_SECTION, "puerto_tcp"))
                try:
                    puerto = int(self.config.get(DEFAULT_SECTION, "puerto_tcp"))
                except:
                    puerto = 502
                    logging.error("Puerto TCP no se encontro en la configuracion. Usando 502 por defecto..")
                conf_eq["ip"] = ip
                conf_eq['port'] = puerto
            else:
                rtu_port = self.config.get(DEFAULT_SECTION, "rtu_port")
                try:
                    baudrate = int(self.config.get(DEFAULT_SECTION, "baudrate"))
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
            """