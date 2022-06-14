from pyModbusTCP import utils

from pyModbusTCP.client import ModbusClient as ModbusClientTCP

import logging
from modbusTCP_DB.config.models import *

logging.getLogger()


class ModbusTCPService:
	def __init__(self, dev_modbus: ConfigModbusDev):
		self.device = dev_modbus
		self.url = dev_modbus.ip
		self.port = dev_modbus.port
		self.cli: ModbusClientTCP

		self.mbId = dev_modbus.id_equipo
		self.name = dev_modbus.nombre_equipo
		self.big_endian = bool(dev_modbus.big_endian)

		self.error = 0
		# Me conecto al equipo
		self.connect()


	def connect(self):
		logging.info(
			f"Creating Modbus TCP Connection to: %s - IP= %s, PUERTO= %i, ID= %s, BIG_ENDIAN= %s, TIMEOUT= %is",
			self.device.nombre_equipo, self.device.ip, self.device.port, self.device.id_equipo,
			str(self.device.big_endian), self.device.timeout)
		self.cli = ModbusClientTCP(host=self.url, port=self.port, unit_id=self.device.id_equipo,
								timeout=self.device.timeout, auto_open=True)
		self.cli.open()
		if self.cli.is_open():
			logging.info("Succesfully connection! :) ")
		else:
			logging.error("Error to connecting! :( ")

		self.readDev()
		for index, item in enumerate(self.device.lecturas):
			print(item.tabla_var)

	def readDev(self):
		for index, item in enumerate(self.device.lecturas):
			self.read(item)

	def read(self, readM: ConfigModbusRead):
		logging.info(f"Leyendo tipo datos %s, tipo registro %s", readM.type, readM.register_type)
		list_16b_regs = None
		if readM is not None:
			read_l = 0
			if readM.type == "UINT32" or readM.type == "INT32" or readM.type == "FLOAT" or readM.type == "SFLOAT":
				read_l = readM.read_len * 2
			else:
				read_l = readM.read_len

			# Lectura segun tipo de registro
			if readM.register_type == "H":				# HOLDING REGISTER
				list_16b_regs = self.cli.read_holding_registers(readM.base_address, read_l)
			elif readM.register_type == "I":			# INPUT REGISTER
				list_16b_regs = self.cli.read_input_registers(readM.base_address, read_l)
			elif readM.register_type == "D":			# DISCRETE INPUT REGISTER
				# read discrete input - bit address  - number of bits to read
				try:
					list_16b_regs = self.cli.read_discrete_inputs(bit_addr=readM.base_address)
				except:
					logging.error("Function  DISCRETE INPUT READ not implemented ")
			elif readM.register_type == "C":			# COIL REGISTER
				# read coils - bit address  - number of bits to read
				try:
					list_16b_regs = self.cli.read_coils(bit_addr=readM.base_address)
				except:
					logging.error("Function READ COILS not implemented ")

			logging.info(f"reading %s len = %s", readM.base_address, read_l)
			logging.info(list_16b_regs)

			if list_16b_regs == None:
				readM.mb_error = readM.mb_error+1
			else:
				readM.mb_error = 0
				convertRead(readM=readM, list_16b_regs=list_16b_regs)


	def update(self):
		logging.info("Updating modbus dev %s ...", self.device.nombre_equipo)
		self.readDev()
		#self.error_var.set_value(self.error)

	def write_value(self, nombre: str, value):
		idx = -1
		found = 0
		for lectura in self.device.lecturas:
			i = 0
			for var in lectura.tabla_nombre_var:
				if var == nombre:
					idx = i
					found = 1
					regs = []
					address = 0
					if lectura.type == "FLOAT":
						address = lectura.base_address + (i * 2)
						reg32b = []
						reg32b.append(utils.encode_ieee(value))
						regs = utils.long_list_to_word(reg32b)
						self.cli.write_multiple_registers(address, regs)
						#for h, reg in enumerate(regs):
						#	self.cli.write_single_register(address+h, int(reg))
						logging.info(f"writing float modbus ip: %s address %s, regs :", self.url, address)
						logging.info(regs)
					elif lectura.type == "SFLOAT":
						address = lectura.base_address + (i * 2)
						reg32b = []
						reg32b.append(utils.encode_ieee(value))
						regs = utils.long_list_to_word(reg32b)
						self.cli.write_multiple_registers(address, regs)
						#for h, reg in enumerate(regs):
						#	self.cli.write_single_register(address+h, int(reg))
						logging.info(f"writing sfloat modbus ip: %s address %s, regs :", self.url, address)
						logging.info(regs)
					else:
						address = lectura.address + i

				i += 1




def convertRead(readM: ConfigModbusRead, list_16b_regs):
	if readM.type == "INT16" or readM.type == "UINT16":
		for i in range(len(readM.tabla_var)):
			readM.tabla_var[i] = list_16b_regs[i]
	elif readM.type == "INT32" or readM.type == "UINT32":
		for i in range((int(readM.read_len))):
			readM.tabla_var[i] = list_16b_regs[(i*2)]*65536+list_16b_regs[(i*2)-1]
	elif readM.type == "SINT32" or readM.type == "SUINT32":
		for i in range((int(readM.read_len))):
			readM.tabla_var[i] = list_16b_regs[(i*2)-1]*65536+list_16b_regs[(i*2)]
	elif readM.type == "FLOAT":
		#list_32b_regs = utils.word_list_to_long(list_16b_regs, big_endian=self.big_endian)
		#list_32b_regs = []
		for i in range((int(readM.read_len))):
			reg32b = list_16b_regs[(i*2)]+list_16b_regs[(i*2)-1]*65536
			readM.tabla_var[i] = utils.decode_ieee(reg32b)
	elif readM.type == "SFLOAT":
		#list_32b_regs = utils.word_list_to_long(list_16b_regs, big_endian=self.big_endian)
		#list_32b_regs = []
		print(list_16b_regs)
		for i in range((int(readM.read_len))):
			#list_32b_regs.append(list_16b_regs[(i*2)-1]*65536+list_16b_regs[(i*2)])
			reg32b = list_16b_regs[(i*2)]*65536+list_16b_regs[(i*2)-1]
			readM.tabla_var[i] = utils.decode_ieee(reg32b)
	# nombres = list(item.keys())
	# for i in range(len(item)):
	# item[nombres[i]] = utils.decode_ieee(list_32b_regs[i])
	# print("Valor["+nombres[i]+"]: "+str(utils.decode_ieee(list_32b_regs[i])))

