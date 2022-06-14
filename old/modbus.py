
from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils

import sys 
import time
from opcua import ua, Server

class Cromatografo_PM:
	def __init__(self, ip, puerto, nombre, opc_obj, opc_id):
		self.url = ip
		self.port = puerto
		self.name = nombre
		self.opc = opc_obj
		self.id = opc_id
	

		self.lectura1 = {
			"C3": 0.0,
			"iC4": 0.0, 
			"nC4": 0.0, 
			"iC5": 0.0, 
			"nC5": 0.0, 
			"N2": 0.0, 
			"C1": 0.0, 
			"CO2": 0.0, 
			"C2": 0.0, 
			"C9": 0.0, 
			"C6": 0.0, 
			"C7": 0.0, 
			"C8": 0.0, 
			"nn1": 0.0, 
			"nn2": 0.0
		}
		self.lectura2 = {
			"CriCondTermTemp": 0.0, 
			"CriCondTermPres": 0.0, 
			"CriCondTermSta": 0.0, 
			"DewPoint1Press": 0.0,
			"DewPoint1Temp": 0.0,
			"DewPoint2Press": 0.0,
			"DewPoint2Temp": 0.0,
			"DewPoint3Press": 0.0,
			"DewPoint3Temp": 0.0
		}
		
		self.dir_lect1 = 7001
		self.dir_lect2 = 7045
		
		self.lecturas = [self.lectura1, self.lectura2]
		self.direcciones = [self.dir_lect1, self.dir_lect2]
		self.longitudes = []
		for item in self.lecturas:
			self.longitudes.append(len(item)*2)
		
		#populating our address space
		self.myobj = self.opc.add_object(self.id, self.name)
		
		self.variables = []
		
		for k,v in self.lectura1.items():
			self.variables.append(self.myobj.add_variable(self.id, k, v))
			
		for k,v in self.lectura2.items():
			self.variables.append(self.myobj.add_variable(self.id, k, v))
		
		#Me conecto al equipo
		self.connect()
		
		
	def connect(self):
		#Me conecto al equipo
		self.cli = ModbusClient(host=self.url, port=self.port, auto_open=True)
		
	def read(self):
		for index, item in enumerate(self.lecturas):
			list_16b_regs = self.cli.read_holding_registers(self.direcciones[index], self.longitudes[index]) 
			list_32b_regs = utils.word_list_to_long(list_16b_regs, big_endian=True)
			nombres = list(item.keys())
			for i in range(len(item)):
				item[nombres[i]] = utils.decode_ieee(list_32b_regs[i])
				#print("Valor["+nombres[i]+"]: "+str(utils.decode_ieee(list_32b_regs[i])))
		
			
	def update(self):
		print("Update...")
		self.read()
		
		index = 0
		for item in self.lecturas:
			nombres = list(item.keys())
			for i in range(len(item)):
				self.variables[index].set_value(item[nombres[i]])
				index = index + 1
				
		


if __name__ == "__main__":
	server = Server()
	server.set_endpoint("opc.tcp://0.0.0.0:4870/server/")
	uri = "http://example.io"
	idx = server.register_namespace(uri)
	
	#get Objects node, this is where we should put our nodes 
	objects = server.get_objects_node()
	
	#declaro al croma
	pmg1 = Cromatografo_PM("10.152.148.28", 502, "PMG1_CROMA", objects, idx)

	Cromatografos = []
	Cromatografos.append(pmg1)

	
	print("Iniciando servidor")
	server.start()
	
	try: 
		count = 0
		while True:
			time.sleep(1)
			for item in Cromatografos:
				item.update()
			
	finally:
		#cierro conexion
		server.stop()

