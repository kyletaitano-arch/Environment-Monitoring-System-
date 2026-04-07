#Kyle was here 
# Anthony was here
# hiiiiiiiiiiiiiiiiii Cmp.
# import smbus2 as smbus
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
TEMP_OUT_L = 0x2A
TEMP_OUT_H = 0x2B
T0_DEGC_X8 = 0x32
T1_DEGC_X8 = 0x33
T0_T1_MSB = 0x35
T0_OUT_L = 0x3C
T0_OUT_H = 0x3D
T1_OUT_L = 0x3E
T1_OUT_H = 0x3F

# Initialize I2C bus
bus = smbus.SMBus(1)

def read_register(reg):
    return bus.read_byte_data(HTS221_ADDRESS, reg)

def write_register(reg, value):
    bus.write_byte_data(HTS221_ADDRESS, reg, value)

def read_temperature():
    # Enable the sensor
    write_register(CTRL_REG1, 0x80)

    # Read calibration data
    T0_degC = read_register(T0_DEGC_X8)
    T1_degC = read_register(T1_DEGC_X8)
    T0_T1_msb = read_register(T0_T1_MSB)
    
    T0_degC |= (T0_T1_msb & 0x03) << 8
    T1_degC |= (T0_T1_msb & 0x0C) << 6
    
    T0_degC /= 8.0
    T1_degC /= 8.0

    # Read temperature raw data
    T0_out = read_register(T0_OUT_L) | (read_register(T0_OUT_H) << 8)
    T1_out = read_register(T1_OUT_L) | (read_register(T1_OUT_H) << 8)
    
    Temp_out = read_register(TEMP_OUT_L) | (read_register(TEMP_OUT_H) << 8)
    if Temp_out > 32767:
        Temp_out -= 65536  # Convert to signed

    # Convert raw value to temperature
    # temperature = T0_degC + (Temp_out - T0_out) * (T1_degC - T0_degC) / (T1_out - T0_out)
    if (T1_out - T0_out) == 0:
        return 0  # or None or default value

    temperature = T0_degC + (Temp_out - T0_out) * (T1_degC - T0_degC) / (T1_out - T0_out)
    return round(temperature, 2)

# Test the sensor
# if __name__ == "__main__":
#     while True:
#         temp = read_temperature()
#         insert_temperature(temp)
#         print(f"Temperature: {temp}°C")
#         time.sleep(1)