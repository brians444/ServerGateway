import pymodbus.exceptions
from pyModbusTCP import utils

from pymodbus.client.sync import ModbusSerialClient as ModbusClientRTU
from modbusTCP_DB.config.models import *
import logging

logging.getLogger()


class ModbusRTUService:
	def __init__(self, dev_modbus: ConfigModbusDev):
		self.device = dev_modbus
		self.client: ModbusClientRTU
		self.baudrate = dev_modbus.baudrate
		self.rtu_port = dev_modbus.rtu_port

		self.cli: ModbusClientRTU
		self.baudrate = dev_modbus.baudrate
		self.rtu_port = dev_modbus.rtu_port


		# MODBUS
		self.mbId = dev_modbus.id_equipo
		self.name = dev_modbus.nombre_equipo
		self.big_endian = bool(dev_modbus.big_endian)

		if self.big_endian:
			self.bit_order = "little"
		else:
			self.bit_order = "big"

		self.error = 0
		# Me conecto al equipo
		self.connect()


	def connect(self):
		logging.info("Conectando modbus dev")
		logging.info(
			f"Creating Modbus RTU Connection to: %s - PUERTO= %s, BAUDRATE= %i, ID= %s, BIG_ENDIAN= %s, TIMEOUT= %is",
			self.device.nombre_equipo, self.device.rtu_port, self.device.baudrate, self.device.id_equipo,
			str(self.device.big_endian), self.device.timeout)
		self.cli = ModbusClientRTU(method="rtu", port=self.rtu_port, baudrate=self.baudrate,
								   unit_id=self.device.id_equipo,
								   timeout=self.device.timeout, auto_open=True, stopbits=1, parity='N', bytesize=8)
		self.cli.connect()
		if self.cli.is_socket_open():
			logging.info("Succesfully connection! :) ")
		else:
			logging.error("Error to connecting! :( ")

		self.readDev()
		for index, item in enumerate(self.device.lecturas):
			print(item.tabla_var)

	def readDev(self):
		logging.info("Reading dev ... ")
		for index, item in enumerate(self.device.lecturas):
			logging.info(f"reading %s", item.tabla_nombre_var)
			self.read(item)
		#self.writeSetpoint()

	def writeSetpoint(self):
		logging.info("Escribiendo setpoints")
		self.write(address=14, value=25.0)
		self.write(address=16, value=22.0)

	def write(self, address: int, value: float):
		reg32b = (utils.encode_ieee(value))
		reg16 = []
		reg16.append(int().from_bytes(reg32b.to_bytes(4, self.bit_order)[:2], self.bit_order))
		reg16.append(int().from_bytes(reg32b.to_bytes(4, self.bit_order)[2:], self.bit_order))
		self.cli.write_registers(address=address, values=reg16)

	def read(self, readM: ConfigModbusRead):
		list_16b_regs = None
		if readM is not None:

			# Calculo la longitud de la lectura
			read_l = 0
			if readM.type == "UINT32" or readM.type == "INT32" or readM.type == "FLOAT" or readM.type == "SFLOAT":
				read_l = readM.read_len * 2
			else:
				read_l = readM.read_len

			# Lectura Modbus - segun tipo de registro
			if readM.register_type == "H":				# HOLDING REGISTER
				list_16b_regs = self.cli.read_holding_registers(address=readM.base_address, count=read_l, unit=int(self.device.id_equipo))
			elif readM.register_type == "I":			# INPUT REGISTER
				list_16b_regs = self.cli.read_input_registers(address=readM.base_address, count=read_l, unit=int(self.device.id_equipo))
			elif readM.register_type == "D":			# DISCRETE INPUT REGISTER
				# read discrete input - bit address  - number of bits to read
				try:
					list_16b_regs = self.cli.read_discrete_inputs(bit_addr=readM.base_address, count=read_l, unit=int(self.device.id_equipo))
				except:
					logging.error("Function  DISCRETE INPUT READ not implemented ")
			elif readM.register_type == "C":			# COIL REGISTER
				# read coils - bit address  - number of bits to read
				try:
					list_16b_regs = self.cli.read_coils(bit_addr=readM.base_address, count=read_l, unit=int(self.device.id_equipo))
				except:
					logging.error("Function READ COILS not implemented ")

			if type(list_16b_regs) == pymodbus.exceptions.ModbusIOException:
				logging.error(f"Error reading: %s", list_16b_regs)
				list_16b_regs = None
			else:
				list_16b_regs = list_16b_regs.registers

			if list_16b_regs == None:
				logging.error(f"Error Reading %s register RTU : address: %s, len: %s, id: %s", readM.register_type,
							readM.base_address, read_l, self.device.id_equipo)
				readM.mb_error = readM.mb_error+1
			else:
				readM.mb_error = 0
				convertRead(readM=readM, list_16b_regs=list_16b_regs)


	def update(self):
		logging.info("Updating modbus dev %s ...", self.device.nombre_equipo)
		self.readDev()
		#self.error_var.set_value(self.error)



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
			readM.tabla_var[i] = float(utils.decode_ieee(reg32b))
	elif readM.type == "SFLOAT":
		#list_32b_regs = utils.word_list_to_long(list_16b_regs, big_endian=self.big_endian)
		#list_32b_regs = []
		for i in range((int(readM.read_len))):
			#list_32b_regs.append(list_16b_regs[(i*2)-1]*65536+list_16b_regs[(i*2)])
			reg32b = list_16b_regs[(i*2)]*65536+list_16b_regs[(i*2)-1]
			readM.tabla_var[i] = float(utils.decode_ieee(reg32b))
	# nombres = list(item.keys())
	# for i in range(len(item)):
	# item[nombres[i]] = utils.decode_ieee(list_32b_regs[i])
	# print("Valor["+nombres[i]+"]: "+str(utils.decode_ieee(list_32b_regs[i])))

