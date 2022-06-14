
import pymodbus.exceptions
from pyModbusTCP import utils

from pyModbusTCP.client import ModbusClient as ModbusClientTCP
from pymodbus.client.sync import ModbusSerialClient

from ctypes import c_uint32, c_uint16

rtu_port = "COM5"
baudrate = 9600
id_equipo = 10
timeout = 5
unit = 10

cli = ModbusSerialClient(method="rtu", port=rtu_port, baudrate=baudrate,
                           timeout=timeout, stopbits=1, parity='N', bytesize=8)
connection = cli.connect()

if connection:
    registers = cli.read_holding_registers(address=10, count=2, unit=unit)
    print(registers)
    registers = cli.read_holding_registers(address=10, count=14, unit=unit)
    print(registers.registers)
    reg = registers.registers
    valores = []

    for i in range(int(len(reg)/2)):
        reg32b = reg[(i * 2)-1] + reg[(i * 2) ] * 65536
        valores.append(float(utils.decode_ieee(reg32b)))

    print("Valores float")
    print(valores)

    # Setpoint high
    reg32b_high = (utils.encode_ieee(25.0))
    # Setpoint low
    reg32b_low = utils.encode_ieee(24.0)
    reg16 = []
    reg16.append(int().from_bytes(reg32b_high.to_bytes(4, "big")[:2], "big"))
    reg16.append(int().from_bytes(reg32b_high.to_bytes(4, "big")[2:], "big"))
    cli.write_registers(address=14, values=reg16)

    reg16 = []
    reg16.append(int().from_bytes(reg32b_low.to_bytes(4, "big")[:2], "big"))
    reg16.append(int().from_bytes(reg32b_low.to_bytes(4, "big")[2:], "big"))
    cli.write_registers(address=16, values=reg16)

    registers = cli.read_holding_registers(address=10, count=14, unit=unit)
    print(registers.registers)

