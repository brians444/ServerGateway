from croma import *
from modbusTCP_DB.old.ups import *

import logging
import time
from opcua import Server
				

if __name__ == "__main__":
	logging.basicConfig()
	log = logging.getLogger('pymodbus.client')
	log.setLevel(logging.ERROR)
	
	server = Server()
	server.set_endpoint("opc.tcp://127.0.0.1:4870/server/")

	# load server certificate and private key. This enables endpoints
	# with signing and encryption.
	
	#server.load_certificate("my_cert.der")
	#server.load_private_key("my_private_key.pem")
	
	uri = "urn:TECNWSCA14:UnifiedAutomation:UaExpert"
	idx = server.register_namespace(uri)
	
	#get Objects node, this is where we should put our nodes 
	objects = server.get_objects_node()
	
	#declaro al croma
	pmg1_ups1 = UPS("127.0.0.1", 502, 1,  "PMG1_UPS_700", objects, idx)
	#pmg1_ups2 = UPS("10.152.148.29", 502, 100,  "PMG1_UPS_701", objects, idx)
	#pmg2_ups = UPS("10.152.138.29", 502, 100,  "PMG2_UPS_001", objects, idx)
	#bat3_ups = UPS("10.152.152.26", 502, 100,  "BAT3_UPS_001", objects, idx)
	UPSs = []
	UPSs.append(pmg1_ups1)
	#UPSs.append(pmg1_ups2)
	#UPSs.append(pmg2_ups)
	#UPSs.append(bat3_ups)
	
	#declaro al croma
	#pmg1 = Cromatografo_PM("10.152.148.28", 502,0, "PMG1_CROMA", objects, idx)

	#Cromatografos = []
	#Cromatografos.append(pmg1)
	
	print("Iniciando servidor")
	server.start()
	
	try: 
		count = 0
		while True:
			time.sleep(10)
			pmg1_ups1.update()
			#for item in Cromatografos:
			#	item.update()
			
	finally:
		#cierro conexion
		server.stop()


