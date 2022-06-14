import typing


class ConfigModbusRead:
    def __init__(self, config_dict):
        self.read_len: int = int(config_dict['read_len'])
        self.address: int = int(config_dict['address'])
        self.type: str = config_dict['type']    # INT16 - UINT16 - INT32 - UINT32 - FLOAT - SWAP FLOAT - DWORD
        self.tabla_nombre_var: typing.List[str] = config_dict['nombres']
        self.register_type = config_dict['register_type']
        self.base_address: int = int(config_dict['base_address'])
        self.file_n: str = str(config_dict['nombre_tabla'])
        self.tabla_var = []
        self.mb_error = 0
        if self.type == "INT16":
            for i in range(len(self.tabla_nombre_var)):
                self.tabla_var.append(int(0))
        elif self.type == "UINT16":
            for i in range(len(self.tabla_nombre_var)):
                self.tabla_var.append(int(0))
        elif self.type == "INT32":
            for i in range(len(self.tabla_nombre_var)):
                self.tabla_var.append(int(0))
        elif self.type == "UINT32":
            for i in range(len(self.tabla_nombre_var)):
                self.tabla_var.append(int(0))
        elif self.type == "FLOAT":
            for i in range(len(self.tabla_nombre_var)):
                self.tabla_var.append(float(0.0))
        elif self.type == "SFLOAT":
            for i in range(len(self.tabla_nombre_var)):
                self.tabla_var.append(float(0.0))
        else:
            for i in range(len(self.tabla_nombre_var)):
                self.tabla_var.append(int(0))


class ConfigModbusDev:
    def __init__(self, config_dict):
        self.type: str = config_dict["type"]
        self.nombre_equipo: str = config_dict['nombre_equipo']
        self.conf_file: str = config_dict['conf_file']
        self.id_equipo = config_dict['id_equipo']
        self.num_lecturas = config_dict['num_lecturas']
        self.bytesize: int = 8
        self.parity: int= 0 # 0 = None - 1 = Even - 2 = Odd
        self.stopbits: int = 1
        if self.type == "tcp":
            self.port = config_dict['port']
            self.ip: str = config_dict['ip']
            self.baudrate = 0
            self.rtu_port: str = "null"
        else:
            self.baudrate: int = config_dict['baudrate']
            self.rtu_port: str = config_dict['rtu_port']
            self.port = 0
            self.ip: str = "null"

        self.timeout: float = float(int(config_dict['timeout'])/1000) # Convierto MS a Seg
        self.lecturas: typing.List[ConfigModbusRead] = config_dict['lecturas']
        if str(config_dict['big_endian']).upper() == "TRUE":
            self.big_endian: bool = True
        else:
            self.big_endian: bool = False

class OpcUaConf:
    def __init__(self, ua_conf):
        self.endpoint_ua: str = ua_conf["endpoint_ua"]
        self.uri: str = ua_conf["uri"]
        self.application_uri: str = ua_conf["application_uri"]
        self.product_uri: str = ua_conf["product_uri"]
        self.name: str = ua_conf["name"]
        self.manufacturer_name: str = ua_conf["manufacturer_name"]

class DatabaseConfig:
    def __init__(self, db_config):
        # self.type: str= db_config["type"]
        self.bucket: str = db_config["bucket"]
        self.org: str = db_config["org"]
        self.token: str = db_config["token"]
        self.port: int = db_config["port"]
        self.url: str = db_config["url"]
        self.name: str = db_config["name"]
