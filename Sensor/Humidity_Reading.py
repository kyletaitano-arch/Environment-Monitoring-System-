# Humidity sensor code 

import smbus
import time

try:
    import smbus # type: ignore
except ImportError:
    class SMBus:
        def __init__(self, bus): pass
        def read_byte_data(self, addr, reg): return 0
        def write_byte_data(self, addr, reg, value): pass

    smbus = type('smbus', (), {'SMBus': SMBus})

HTS221_ADDRESS = 0x5F
CTRL_REG1 = 0x20

# Humidity registers
HUMIDITY_OUT_L = 0x28
HUMIDITY_OUT_H = 0x29
H0_RH_X2 = 0x30
H1_RH_X2 = 0x31
H0_T0_OUT_L = 0x36
H0_T0_OUT_H = 0x37
H1_T0_OUT_L = 0x3A
H1_T0_OUT_H = 0x3B

# Initialize I2C bus
bus = smbus.SMBus(1)

def read_register(reg):
    return bus.read_byte_data(HTS221_ADDRESS, reg)

def write_register(reg, value):
    bus.write_byte_data(HTS221_ADDRESS, reg, value)

def read_humidity():
    # Enable the sensor
    write_register(CTRL_REG1, 0x80)

    # Read calibration values
    H0_rH = read_register(H0_RH_X2) / 2.0
    H1_rH = read_register(H1_RH_X2) / 2.0

    H0_T0_out = read_register(H0_T0_OUT_L) | (read_register(H0_T0_OUT_H) << 8)
    H1_T0_out = read_register(H1_T0_OUT_L) | (read_register(H1_T0_OUT_H) << 8)

    # Convert to signed
    if H0_T0_out > 32767:
        H0_T0_out -= 65536
    if H1_T0_out > 32767:
        H1_T0_out -= 65536

    # Read raw humidity
    H_out = read_register(HUMIDITY_OUT_L) | (read_register(HUMIDITY_OUT_H) << 8)
    if H_out > 32767:
        H_out -= 65536

    # Avoid division by zero
    if (H1_T0_out - H0_T0_out) == 0:
        return 0

    # Convert to % relative humidity
    humidity = H0_rH + (H_out - H0_T0_out) * (H1_rH - H0_rH) / (H1_T0_out - H0_T0_out)

    return round(humidity, 2)
#Test Code 
if __name__ == "__main__":
    while True:
        humid=read_humidity()
        print(f"Humidity: {humid}%")
        time.sleep(30) 