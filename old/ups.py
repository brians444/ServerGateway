
import struct
from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils



class UPS:
	def __init__(self, ip, puerto, mb_id, nombre, opc_obj, opc_id):
		self.url = ip
		self.port = puerto
		self.mbId = mb_id
		self.name = nombre
		self.opc = opc_obj
		self.id = opc_id
		
		self.error = 0

		self.lectura1 = {
			"ChargerIca_a": 0.0,
			"ChargerIca_b": 0.0, 
			"ChargerIca_c": 0.0, 
			"ChargerVca_a": 0.0, 
			"ChargerVca_b": 0.0, 
			"ChargerVca_c": 0.0, 
			"ChargerFreqInput": 0.0, 
			"ChargerBatIcc": 0.0, 
			"ChargerBatVcc": 0.0, 
			"ChargerRectifierIcc": 0.0, 
			"ChargerRectifierVcc": 0.0, 
			"ChargerMinAuto": 0.0, 
			"ChargerPotActive": 0.0, 
			"ChargerPotLoadFactor": 0.0, 
			"ChargerPotOut": 0.0, 
			"ChargerModeFunc": 0,
			"ChargerLoadState": 0, 
			"ChargerAlarms1": 0, 
			"ChargerAlarms2": 0, 
			"ChargerAlarms3": 0
		}
		
		self.lectura2 = {
			"InvAlarms1": 0, 
			"InvAlarms1": 0
		}
		
		self.lectura3 = {
			"InvIOut_a": 0.0,
			"InvIOut_b": 0.0, 
			"InvIOut_c": 0.0, 
			"InvVccIn": 0.0, 
			"InvIccIn": 0.0, 
			"InvPotOut": 0.0, 
			"InvFreqOut": 0.0
		}
		
		self.lectura4 = {
			"ConmutadorIout_a": 0.0,
			"ConmutadorIout_b": 0.0, 
			"ConmutadorIout_c": 0.0, 
			"ConmutadorFreqInv": 0.0, 
			"ConmutadorIinv_a": 0.0, 
			"ConmutadorIinv_b": 0.0, 
			"ConmutadorIinv_c": 0.0, 
			"ConmutadorFreqLine": 0.0, 
			"ConmutadorILine_a": 0.0, 
			"ConmutadorILine_b": 0.0, 
			"ConmutadorILine_c": 0.0, 
			"ConmutadorVacOut_a": 0.0, 
			"ConmutadorVacOut_b": 0.0, 
			"ConmutadorVacOut_c": 0.0, 
			"ConmutadorVacInv_a": 0,
			"ConmutadorVacInv_b": 0, 
			"ConmutadorVacInv_c": 0, 
			"ConmutadorVacLine_a": 0, 
			"ConmutadorVacLine_b": 0, 
			"ConmutadorVacLine_c": 0, 
			"ConmutadorPotOut": 0, 
			"ConmutadorPotOut": 0, 
			"ConmutadorByPassOK": 0, 
			"ConmutadorInvOK": 0, 
			"ConmutadorByPassConnected": 0, 
			"ConmutadorInvConnected": 0, 
			"ConmutadorInvSincro": 0, 
			"ConmutadorAlarms1": 0, 
			"ConmutadorAlarms1": 0, 
			"nn": 0, 
			"ConmutadorMode": 0
			
		}
		
		self.dir_lect1 = 44
		self.dir_lect2 = 5007
		self.dir_lect3 = 5025
		self.dir_lect4 = 6020
		
		
		self.lecturas = [self.lectura1, self.lectura2, self.lectura3, self.lectura4]
		self.direcciones = [self.dir_lect1, self.dir_lect2, self.dir_lect3, self.dir_lect4]
		self.longitudes = []
		for item in self.lecturas:
			self.longitudes.append(len(item))
		
		#populating our address space
		self.myobj = self.opc.add_object(self.id, self.name)
		
		self.variables = []
		
		for item in self.lecturas:
			for k,v in item.items():
				self.variables.append(self.myobj.add_variable(self.id, k, v))
		
		self.error_var = self.myobj.add_variable(self.id, "error_count", 0)
		#Me conecto al equipo
		self.connect()
		
		
	def connect(self):
		#Me conecto al equipo
		self.cli = ModbusClient(host=self.url, port=self.port, unit_id= self.mbId, auto_open=True, timeout= 0.5)
		
	def read(self):
		for index, item in enumerate(self.lecturas):
			list_16b_regs = self.cli.read_holding_registers(self.direcciones[index], self.longitudes[index]) 
			if(list_16b_regs == None):
				self.error = self.error+1
			else:
				self.error = 0
				#list_32b_regs = utils.word_list_to_long(list_16b_regs, big_endian=True)
				nombres = list(item.keys())
				for i in range(len(item)):
					item[nombres[i]] = list_16b_regs[i]
					#item[nombres[i]] = utils.decode_ieee(list_32b_regs[i])
					#print("Valor["+nombres[i]+"]: "+str(utils.decode_ieee(list_32b_regs[i])))
		
			
	def update(self):
		print("Update...")
		self.read()
		self.error_var.set_value(self.error)
		
		index = 0
		for item in self.lecturas:
			nombres = list(item.keys())
			for i in range(len(item)):
				self.variables[index].set_value(item[nombres[i]])
				index = index + 1
				
